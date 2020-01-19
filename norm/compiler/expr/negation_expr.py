from typing import List
from norm.compiler import NormCompilable, Variable
from norm.grammar.normParser import normParser


class NegationExpr(NormCompilable):

    def compile(self, compound_expr):
        """
        :type compound_expr: normParser.CompoundExprContext
        :rtype: List[norm.executable.NormExecutable]
        """
        pass

