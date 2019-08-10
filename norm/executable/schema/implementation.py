from pandas import DataFrame, Series, Index

from norm.executable import NormExecutable
from norm.executable.schema.declaration import TypeDeclaration
from norm.executable.expression import NormExpression
from norm.models import Lambda, Status

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

    def compile(self, context):
        """
        Three types of implementations
            * new implementation (:=) removes all revisions from this version
            * conjunctive implementation (&=)
            * disjunctive implementation (|=)
        """
        lam = self.type_.lam
        if lam.status != Status.DRAFT:
            logger.info('Lambda: {} is not in DRAFT mode. Import first'.format(lam))
            lam = Lambda(namespace=context.context_namespace, name=lam.name, description=lam.description,
                         variables=lam.variables, user=context.user)
        if self.description is not None and self.description.strip() != '':
            self.query.description = self.description
        self.lam = lam
        return self

    def execute(self, context):
        from norm.engine import ImplType
        from norm.models.norm import RevisionType
        lam = self.lam
        delta = self.query.execute(context)
        if isinstance(delta, Lambda):
            delta = delta.data
        if isinstance(delta, DataFrame):
            delta = delta.copy()
            if self.query.lam is not self.lam and self.lam is not self.query.lam.cloned_from:
                # reset the index name if the output lambda is not the lambda to be revised
                delta.index.name = ''

            if delta.index.name != lam.VAR_OID:
                delta = lam.fill_primary(delta)
                delta = lam.fill_time(delta)
                delta = lam.fill_oid(delta)
        elif isinstance(delta, Index):
            assert(delta.name == lam.VAR_OID)
            cols = [v.name for v in lam.variables if v.name in self.query.lam]
            delta = self.query.lam.data.loc[delta, cols]
            delta = lam.fill_primary(delta)
            delta = lam.fill_time(delta)
            delta = lam.fill_oid(delta.reset_index(drop=True))
        qs = str(self.query)
        if self.op == ImplType.DEF:
            # If the query already exists, the revision is skipped
            if any((rev.query == qs for rev in lam.revisions)):
                return lam

            # Ensure the Lambda is a new implementation
            if len(lam.revisions) > 0:
                lam.remove_revisions()
            lam.revise(qs, self.description, delta, RevisionType.DISJUNCTION)
        elif self.op == ImplType.OR_DEF:
            lam.revise(qs, self.description, delta, RevisionType.DISJUNCTION)
        elif self.op == ImplType.AND_DEF:
            if isinstance(delta, Series):
                if len(delta) == 1:
                    vname = delta.name
                    vvalue = delta.values[0]
                    delta = DataFrame(index=lam.data.index)
                    delta[vname] = vvalue
                    delta = lam.fill_time(delta)
                elif delta.index.name == lam.VAR_OID:
                    delta = DataFrame(delta)
                    delta = lam.fill_time(delta)
            elif isinstance(delta, DataFrame):
                delta = lam.fill_time(delta)
            lam.revise(qs, self.description, delta, RevisionType.CONJUNCTION)
        return lam
