from norm.executable.expression.evaluation import EvaluationExpr
from norm.grammar.literals import AOP
from norm.executable import NormError
from norm.executable.expression import NormExpression

import logging

from norm.models import Lambda, Variable

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
            if isinstance(self.expr1, EvaluationExpr) and self.expr1.variable is None and len(self.expr1.args) == 1:
                # It is possible to be parsed as arguments
                self.expr1 = self.expr1.args[0].expr
        if isinstance(self.expr2, EvaluationExpr) and self.expr2.variable is None and len(self.expr2.args) == 1:
            # It is possible to be parsed as arguments
            self.expr2 = self.expr2.args[0].expr

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
            from norm.models import lambdas
            self.lam = Lambda(variables=[Variable.create(variable.name, lambdas.Any)])
            self.lam.df = context.scope.df.copy()
            self.lam.df[variable.name] = self.lam.df.eval(self._exprstr)
            return self.lam
        self.lam = context.scope
        return self.lam
