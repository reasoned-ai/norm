from norm.compiler import NormCompilable
from norm.grammar.normParser import normParser


class CodeExpr(NormCompilable):

    def compile(self, code_expr):
        """
        :type code_expr: normParser.CodeExprContext
        :rtype: List[NormExecutable]
        """
        pass

