import pandas as pd
from pandas import DataFrame

from norm.executable.schema import NormSchema
from norm.executable.schema.declaration import TypeDeclaration
from norm.executable.expression import NormExpression
from norm.models import Lambda, Status, Variable
from norm.utils import hash_df

import logging
logger = logging.getLogger(__name__)


class TypeImplementation(NormSchema):

    def __init__(self, type_, op, query, description):
        """
        The implementation of a type. Depending on the operation, it can be initial implementation or
        incremental implementation.
        :param type_: the type to implement
        :type type_: TypeDeclaration
        :param op: the operation of the implementation, i.e., [':=', '|=', '&=']
        :type op: ImplType
        :param query: the query expression that implements the type
        :type query: NormExpression
        :param description: the implementation documentation. it will be appended to original one for incremental.
        :type description: str
        """
        super().__init__()
        self.type_ = type_
        self.op = op
        self.query = query
        self.description = description

    def compile(self, context):
        """
        Three types of implementations
            * new implementation (:=) implies an anchor version
              if the existing one is cloned or has at least one revision.
            * conjunctive implementation (&=)
            * disjunctive implementation (|=)
        """
        lam = self.type_.lam
        if lam.status != Status.DRAFT:
            logger.info('Lambda: {} is not in DRAFT mode. Import first'.format(lam))
            lam = Lambda(namespace=context.context_namespace, name=lam.name, description=lam.description,
                         variables=lam.variables, user=context.user)
        if self.description is not None or self.description.strip() != '':
            self.query.description = self.description
        self.lam = lam
        if context.scope is None:
            context.scope = lam
        return self

    def execute(self, context):
        from norm.engine import ImplType
        lam = self.lam
        if self.op == ImplType.DEF:
            # Ensure the Lambda is a new implementation
            if len(lam.revisions) > 0:
                lam.remove_revisions()
            to_append = self.query.execute(context)
            if isinstance(to_append, DataFrame):
                lam.add_data(hash_df(to_append), to_append)
        elif self.op == ImplType.OR_DEF:
            to_append = self.query.execute(context)
            if isinstance(to_append, DataFrame):
                lam.add_data(hash_df(to_append), to_append)
        elif self.op == ImplType.AND_DEF:
            to_concat = self.query.execute(context)
            if isinstance(to_concat, DataFrame) and len(lam.data) == len(to_concat):
                lam.df = pd.concat([lam.df, to_concat], axis=1)
            else:
                if len(self.query.projection.variables) == 1:
                    lam.df[self.query.projection.variables[0].name] = to_concat
                else:
                    for i, v in enumerate(self.query.projection.variables):
                        lam.df[v.name] = to_concat[i]
            # Add new variables automatically
            # TODO: need a better type inference
            from norm.models import lambdas
            any_type = lambdas.Any
            lam.add_variable([Variable(v.name, any_type) for v in self.query.projection.variables
                              if v.name not in lam])
        return lam
