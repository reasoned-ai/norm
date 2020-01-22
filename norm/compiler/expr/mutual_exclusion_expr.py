from norm.compiler import NormCompiler
from norm.executable import NormExecutable
from norm.grammar.normParser import normParser


def compile_mutual_exclusive(compiler, left_expr, right_expr):
    """
    Compile mutual exclusive relation between two expressions
    :type compiler: NormCompiler
    :type left_expr: normParser.CompoundExprContext
    :type right_expr: normParser.CompoundExprContext
    :rtype: NormExecutable
    """
    pass


