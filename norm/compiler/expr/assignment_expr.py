from typing import List
from norm.compiler import NormCompilable, Variable
from norm.grammar.normParser import normParser


class AssignmentExpr(NormCompilable):

    def compile(self, compound_expr, variables):
        """
        :type compound_expr: normParser.CompoundExprContext or normParser.SimpleExprContext
        :type variables: List[Variable]
        :rtype: norm.executable.NormExecutable
        """
        pass

