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
        self.data = context.scope.data
        self.output_lam = context.scope.output_type
        return self

    def execute(self, context):
        df = self.data.eval(self._exprstr)
        if self.projection and self.projection.num > 0:
            from pandas import DataFrame, Series
            if isinstance(df, DataFrame):
                self.data = df.renames({old_name: new_var.name for old_name, new_var in
                                        zip(df.columns, self.projection.variables)})
            elif isinstance(df, Series):
                self.data = DataFrame({self.projection.variables[0].name: df})
        else:
            self.data = df
        return self.data
