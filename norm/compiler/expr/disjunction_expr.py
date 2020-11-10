from norm.compiler import NormCompiler
from norm.parser.normParser import normParser
from norm.executable import NormExecutable


def compile_disjunction(compiler, left_expr, right_expr):
    """
    Compile disjunctive relation between two expressions
    :type compiler: NormCompiler
    :type left_expr: normParser.CompoundExprContext
    :type right_expr: normParser.CompoundExprContext
    :rtype: NormExecutable
    """
    pass


