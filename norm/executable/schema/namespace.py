from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from norm.executable import NormExecutable, NormError
from norm.executable.schema.type import TypeName

from norm.models import Status

import logging

from norm.models.norm import new_version

logger = logging.getLogger(__name__)


class Import(NormExecutable):

    def __init__(self, namespace=None, type_=None, variable=None):
        """
        Import the namespace, if the variable name is given, the imported type is cloned to the
        current context with the variable name
        :param namespace: the namespace
        :type namespace: str
        :param type_: the type
        :type type_: TypeName
        :param variable: the variable
        :type variable: str
        """
        super().__init__()
        assert(namespace is not None)
        assert(namespace != '')
        self.namespace = namespace
        self.type_ = type_
        self.variable = variable

    def compile(self, context):
        """
        Imports follow the following logic:
            * imported namespace is stored in the context
            * imported type is cloned in the context namespace as a draft
            * imported type with alias is cloned and renamed in the context namespace as a draft
        """
        if self.namespace not in context.search_namespaces:
            context.search_namespaces.append(self.namespace)
        if self.type_:
            if self.type_.namespace != self.namespace:
                self.type_.namespace = self.namespace
                self.type_.compile(context)  # require a recompilation since namespace has been changed
            lam = self.type_.lam
            if lam is None:
                msg = "Can not find the type {} in namespace {}".format(self.type_.name, self.namespace)
                logger.error(msg)
                raise NormError(msg)
            if self.variable:
                alias = lam.clone()
                alias.namespace = context.context_namespace
                alias.name = self.variable
                context.session.add(alias)
                self.lam = alias
            else:
                self.lam = lam
        else:
            from norm.models.norm import Lambda, Variable
            from norm.models import lambdas

            lams = context.session.query(Lambda).filter(Lambda.namespace.startswith(self.namespace)).all()
            self.lam = context.temp_lambda([Variable('namespace', lambdas.String),
                                            Variable('name', lambdas.String),
                                            Variable('description', lambdas.String),
                                            Variable('latest', lambdas.String, primary=True),
                                            Variable('num_versions', lambdas.Integer),
                                            Variable('variables', lambdas.String),
                                            Variable('num_args', lambdas.Integer),
                                            Variable('owner', lambdas.String),
                                            Variable('created_on', lambdas.Datetime, as_time=True),
                                            Variable('changed_on', lambdas.Datetime)])

            if len(lams) > 0:
                from pandas import DataFrame
                results = DataFrame(data=[{'namespace': lam.namespace, 'name': lam.name, 'description': lam.description,
                                           'latest': lam.version,
                                           'variables': ', '.join(['{}:{}'.format(v.name, v.type_.name)
                                                                   for v in lam.variables]),
                                           'num_args': lam.nargs,
                                           'owner': lam.owner, 'created_on': lam.created_on,
                                           'changed_on': lam.changed_on} for lam in lams])
                p = r'{}[^\.]+\.'.format(self.namespace)
                results = results.drop(results[results.namespace.str.match(p)].index)
                agg_results = results.groupby(['namespace', 'name']).agg({'latest': ['max', 'count']})\
                    .reset_index(drop=True)
                agg_results.columns = ["latest", "num_versions"]
                results = agg_results.join(results.set_index('latest'), on='latest')
                results = results[[v.name for v in self.lam.variables]]
                results = self.lam.fill_oid(results)
                results = self.lam.fill_time(results)
                self.lam.data = results
                for n in results.namespace.unique():
                    if n not in context.search_namespaces:
                        context.search_namespaces.append(n)
        return self


class Export(NormExecutable):

    def __init__(self, namespace=None, type_=None, alias=None):
        """
        Export the type to the namespace
        :param namespace: the namespace
        :type namespace: str or None
        :param type_: the type
        :type type_: TypeName
        :param alias: the alias in the namespace
        :type alias: str or None
        """
        super().__init__()
        assert(type_ is not None)
        self.namespace = namespace
        self.type_ = type_
        self.alias = alias

    def compile(self, context):
        session = context.session
        lam = self.type_.lam
        if lam is None:
            msg = "Can not find the type {} in namespace {}".format(self.type_.name, self.type_.namespace)
            logger.error(msg)
            raise NormError(msg)
        if lam.status != Status.DRAFT:
            msg = 'Type {} is not in the draft status'
            logger.error(msg)
            raise NormError(msg)

        if self.namespace is None or self.namespace.strip() == '':
            if lam.cloned_from:
                lam.namespace = lam.cloned_from.namespace
            else:
                lam.namespace = context.user_namespace
        else:
            lam.namespace = self.namespace

        old_lam_name = lam.name
        if self.alias:
            lam.name = self.alias
        lam.version = new_version()
        lam.status = Status.READY
        lam.owner = context.user
        lam.created_on = datetime.utcnow()
        lam.changed_on = datetime.utcnow()
        lam.save()

        # clone this one back to the current context for further modification
        new_lam = lam.clone()
        new_lam.namespace = context.context_namespace
        new_lam.name = old_lam_name
        session.add(new_lam)
        from norm.config import cache
        cache[(context.context_namespace, new_lam.name, None, None)] = new_lam
        # TODO: possible cascaded exporting. the clone_from object might need to be exported too, or merge into one.

        self.lam = lam
        return self


