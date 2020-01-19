from typing import List
from norm.compiler import NormCompilable, Variable
from norm.grammar.normParser import normParser


class RandomGenerationExpr(NormCompilable):

    def compile(self, compound_expr, variables):
        """
        :type compound_expr: normParser.CompoundExprContext
        :type variables: List[Variable]
        :rtype: List[norm.executable.NormExecutable]
        """
        pass

