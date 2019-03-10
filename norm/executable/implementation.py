from norm.executable import NormExecutable, NormError
from norm.executable.expression import NormExpression
from norm.models import Lambda


class TypeImplementation(NormExecutable):

    def __init__(self, type_, op, query, description):
        """
        The implementation of a type. Depending on the operation, it can be initial implementation or
        incremental implementation.
        :param type_: the type to implement
        :type type_: TypeName
        :param op: the operation of the implementation, i.e., ['=', '|=', '&=']
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
            * new implementation (=) implies an anchor version
              if the existing one is cloned or has at least one revision.
            * conjunctive implementation (&=)
            * disjunctive implementation (|=)
        """
        session = context.session
        from norm.engine import ImplType
        lam = None
        if self.op == ImplType.ASS:
            lam = self.type_.lam
            if lam is None:
                #  Create a new Lambda
                lam = Lambda(namespace=context.context_namespace, name=self.type_.name)
                session.add(lam)
            # TODO
            lam.conjunction()
        elif self.op == ImplType.ORAS:
            pass
        elif self.op == ImplType.ANDAS:
            pass
        else:
            msg = 'Implementation only supports =, &=, |= for now'
            raise NormError(msg)
        self.lam = lam
        return self

    def execute(self, context):
        return self.lam
