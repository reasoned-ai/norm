from typing import List
from norm.compiler import NormCompilable, Variable
from norm.grammar.normParser import normParser


class ImplicationExpr(NormCompilable):

    def compile(self, left_expr, right_expr):
        """
        :type left_expr: normParser.CompoundExprContext
        :type right_expr: normParser.CompoundExprContext
        :rtype: List[norm.executable.NormExecutable]
        """
        pass

