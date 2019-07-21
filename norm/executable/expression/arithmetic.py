import uuid

from norm.grammar.literals import AOP
from norm.executable import NormError
from norm.executable.expression import NormExpression
from norm.executable.expression.evaluation import EvaluationExpr

import logging

logger = logging.getLogger(__name__)


class ArithmeticExpr(NormExpression):

    def __init__(self, op, expr1, expr2=None, projection=None):
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
        self.op: AOP = op
        self.expr1: ArithmeticExpr = expr1
        self.expr2: ArithmeticExpr = expr2
        self.projection = projection
        self._projection_name = None
        assert(self.op is not None)
        assert(self.expr2 is not None)
        self._exprstr: str = None

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

        if self.op is AOP.SUB and self.expr1 is None:
            self._exprstr = '-({})'.format(self.expr2)
        else:
            self._exprstr = '({}) {} ({})'.format(self.expr1, self.op, self.expr2)
        self.eval_lam = context.scope
        from norm.models import Lambda, Variable, lambdas
        if self.projection and self.projection.num > 0:
            self._projection_name = self.projection.variables[0].name
        else:
            self._projection_name = Lambda.VAR_OUTPUT
        self.lam = context.temp_lambda([Variable(self._projection_name, lambdas.Any)])
        self.lam.cloned_from = self.eval_lam
        return self

    def execute(self, context):
        df = self.eval_lam.data.eval(self._exprstr)
        if self.projection and self.projection.num > 0:
            from pandas import DataFrame, Series
            if isinstance(df, DataFrame):
                raise NormError('cant be here')
                self.data = df.renames({old_name: new_var.name for old_name, new_var in
                                        zip(df.columns, self.projection.variables)})
        assert(isinstance(df, Series))
        self.lam.data = DataFrame({self._projection_name: df})
        return self.lam.data
