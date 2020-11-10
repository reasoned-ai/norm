from norm.compiler import NormCompiler
from norm.compiler.expr.evaluation_expr import compile_evaluation_expr
from norm.executable import NormExecutable
from norm.parser.normParser import normParser
from typing import Optional


def compile_arithmetic_expr(compiler: NormCompiler,
                            arithmetic_expr: normParser.ArithmeticExprContext
                            ) -> Optional[NormExecutable]:
    if arithmetic_expr.evaluationExpr():
        return compile_evaluation_expr(compiler, arithmetic_expr.evaluationExpr())
    else:
        # TODO: others
        return None
