import pandas as pd
from pandas import DataFrame

from norm.executable import NormExecutable, NormError
from norm.executable.declaration import TypeDeclaration
from norm.executable.expression import NormExpression
from norm.executable.expression.evaluation import EvaluationExpr
from norm.models import Lambda, Status, Variable, retrieve_type

import logging
logger = logging.getLogger(__name__)


class TypeImplementation(NormExecutable):

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
        self.lam = None

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
        elif self.op == ImplType.OR_DEF:
            pass
        elif self.op == ImplType.AND_DEF:
            to_concat = self.query.execute(context)
            if isinstance(to_concat.data, DataFrame) and len(lam.data) == len(to_concat.data):
                lam.df = pd.concat([lam.data, to_concat], axis=1)
            else:
                if len(self.query.projection.variables) == 1:
                    vn = self.query.projection.variables[0].name
                    lam.df[vn] = to_concat.data
                    if vn not in lam:
                        lam.add_variable(Variable.create(vn, retrieve_type('norm.native', 'Any')))
                else:
                    for i, v in enumerate(self.query.projection.variables):
                        lam.df[v.name] = to_concat.data[i]
            return lam
        return self.query.execute(context)
