from norm.executable import NormExecutable
from norm.executable.expression import NormExpression


class SliceExpr(NormExpression):

    def __init__(self, expr, start, end):
        """
        Slice the expression results
        :param expr: the expression to evaluate
        :type expr: NormExpression
        :param start: the start position
        :type start: int
        :param end: the end position
        :type end: int
        """
        super().__init__()
        self.expr: NormExpression = expr
        self.start: int = start
        self.end: int = end

    def compile(self, context):
        self.expr = self.expr.compile(context)
        from norm.executable.schema.variable import VariableName
        from norm.executable.expression.evaluation import EvaluationExpr
        if isinstance(self.expr, VariableName):
            self.expr = EvaluationExpr(args=[], variable=self.expr).compile(context)
        return self

    def execute(self, context):
        df = self.expr.execute(context)
        df = df.iloc[self.start:self.end].reset_index(drop=True)
        # TODO whether reset the index for the projected variable or not?
        return df


class EvaluatedSliceExpr(SliceExpr):

    def __init__(self, expr, expr_range):
        """
        Slice the expression with a range evaluation expression
        :param expr: the expression to slice
        :type expr: NormExpression
        :param expr_range: the expression to evaluate
        :type expr_range: NormExpression
        """
        super().__init__(expr, 0, -1)
        self.expr_range = expr_range
