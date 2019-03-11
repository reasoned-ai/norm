import uuid

from norm.executable import NormExecutable, NormError
from norm.executable.type import TypeName

from norm.models import Status

import logging
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
        self.lam = None

    def compile(self, context):
        """
        Imports follow the following logic:
            * imported namespace is stored in the context
            * imported type is cloned in the context namespace as a draft
            * imported type with alias is cloned and renamed in the context namespace as a draft
        """
        context.search_namespaces.add(self.namespace)
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
        return self

    def execute(self, context):
        if self.type_ is None:
            # TODO: should figure out returning of namespace since it is not a Lambda
            return self.namespace
        else:
            return self.lam


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
        self.lam = None

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
        # TODO: version has to be set here instead of at the commitment time. need to verify.
        lam.version = str(uuid.uuid4())
        lam.status = Status.READY

        # clone this one back to the current context for further modification
        new_lam = lam.clone()
        new_lam.namespace = context.context_namespace
        new_lam.name = old_lam_name
        session.add(new_lam)

        # TODO: possible cascaded exporting. the clone_from object might need to be exported too, or merge into one.
        self.lam = lam
        return self

    def execute(self, context):
        return self.lam

