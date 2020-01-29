from norm.compiler import NormCompiler
from norm.compiler.expr.compound_expr import compile_compound_expr
from norm.grammar.normParser import normParser
from norm.executable import NormExecutable


def compile_conjunction(compiler, left_expr, right_expr):
    """
    Compile conjunctive relations between two expressions
    :type compiler: NormCompiler
    :type left_expr: normParser.CompoundExprContext
    :type right_expr: normParser.CompoundExprContext
    :rtype: NormExecutable
    """
    left_exe = compile_compound_expr(compiler, left_expr)
    right_exe = compile_compound_expr(compiler, right_expr)

    pass


