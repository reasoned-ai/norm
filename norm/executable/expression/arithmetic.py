from norm.literals import AOP
from norm.executable import NormError
from norm.executable.expression import NormExpression

import logging
logger = logging.getLogger(__name__)


class ArithmeticExpr(NormExpression):

    def __init__(self, op, expr1, expr2=None):
        """
        Arithmetic expression
        :param op: the operation, e.g., [+, -, *, /, %, **]
        :type op: AOP
        :param expr1: left expression
        :type expr1: ArithmeticExpr
        :param expr2: right expression
        :type expr2: ArithmeticExpr
        """
        super().__init__()
        self.op = op
        self.expr1 = expr1
        self.expr2 = expr2
        assert(self.op is not None)
        assert(self.expr2 is not None)
        self._exprstr = None

    def __str__(self):
        if self._exprstr is None:
            msg = 'Compile the expression first'
            logger.error(msg)
            raise NormError(msg)
        return self._exprstr

    def compile(self, context):
        if self.expr1:
            self.expr1 = self.expr1.compile(context)
        self.expr2 = self.expr2.compile(context)
        if self.op is AOP.SUB:
            self._exprstr = '-({})'.format(self.expr2)
        else:
            self._exprstr = '({}) {} ({})'.format(self.expr1, self.op, self.expr2)
        return self

    def serialize(self):
        pass

    def execute(self, context):
        if self.projection and self.projection.num() >= 1:
            variable = self.projection.variables[0]
            # TODO: add a column to the schema?
            df = context.scope.df
            df[variable.name] = df.eval(self._exprstr)
