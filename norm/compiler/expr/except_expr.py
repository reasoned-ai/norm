from norm.compiler import NormCompiler
from norm.executable import Difference
from norm.executable import NormExecutable
from norm.grammar.normParser import normParser


def compile_except(compiler, left_expr, right_expr):
    """
    Compile except relations between two expressions
    :type compiler: NormCompiler
    :type left_expr: normParser.CompoundExprContext
    :type right_expr: normParser.CompoundExprContext
    :rtype: NormExecutable
    """
    from norm.compiler.expr.compound_expr import compile_compound_expr
    return Difference(compiler, dependents=[compile_compound_expr(compiler, left_expr),
                                            compile_compound_expr(compiler, right_expr)])


