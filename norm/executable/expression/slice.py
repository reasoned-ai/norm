from norm.executable import NormExecutable
from norm.executable.expression import NormExpression


class SliceExpr(NormExpression):

    def __init__(self, expr, start, end):
        """
        Slice the expression results
        :param expr: the expression to evaluate
        :type expr: NormExecutable
        :param start: the start position
        :type start: int
        :param end: the end position
        :type end: int
        """
        super().__init__()
        self.expr = expr
        self.start = start
        self.end = end

    def compile(self, context):
        self.expr = self.expr.compile(context)
        return self

    def serialize(self):
        pass

    def execute(self, context):
        lam = self.expr.execute(context)
        df = lam.df.iloc[self.start:self.end]
        # TODO reset the index for the projected variable
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

    def execute(self, context):
        raise NotImplementedError
