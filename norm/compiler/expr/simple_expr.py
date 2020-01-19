from typing import List
from norm.compiler import NormCompilable
from norm.grammar.normParser import normParser


class SimpleExpr(NormCompilable):

    def compile(self, simple_expr):
        """
        :type simple_expr: normParser.SimpleExprContext
        :rtype: List[NormExecutable]
        """
        pass

