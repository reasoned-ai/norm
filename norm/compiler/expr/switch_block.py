from norm.compiler import NormCompiler
from norm.executable import NormExecutable
from norm.parser.normParser import normParser


def compile_switch_block(compiler, left_expr, right_expr):
    """
    Compile a block of switch conditions, if..elif..else
    :type compiler: NormCompiler
    :type left_expr: normParser.CompoundExprContext
    :type right_expr: normParser.CompoundExprContext
    :rtype: NormExecutable
    """
    pass


