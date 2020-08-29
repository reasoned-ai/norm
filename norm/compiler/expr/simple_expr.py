from norm.compiler import NormCompiler
from norm.compiler.expr.arithmetic_expr import compile_arithmetic_expr
from norm.executable import NormExecutable
from norm.grammar.normParser import normParser
from typing import Optional


def compile_simple_expr(compiler: NormCompiler, simple_expr: normParser.SimpleExprContext) -> Optional[NormExecutable]:
    if simple_expr.comparisonOperator():
        lhs = simple_expr.arithmeticExpr(0)
        rhs = simple_expr.arithmeticExpr(1)
        ops = simple_expr.comparisonOperator().getText()
        # TODO
        pass
    else:
        return compile_arithmetic_expr(compiler, simple_expr.arithmeticExpr(0))


