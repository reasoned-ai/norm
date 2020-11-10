from norm.compiler import NormCompiler
from norm.compiler.expr.query_expr import compile_query_expr
from norm.compiler.expr.constant_expr import compile_constant_expr
from norm.executable import NormExecutable
from norm.executable.expression.constant import Constant, MeasurementConstant
from norm.parser.normParser import normParser
from typing import Optional


def compile_evaluation_expr(compiler: NormCompiler,
                            evaluation_expr: normParser.EvaluationExprContext
                            ) -> Optional[NormExecutable]:
    if evaluation_expr.queryExpr():
        return compile_query_expr(compiler, evaluation_expr.queryExpr())
    elif evaluation_expr.constant():
        return compile_constant_expr(compiler, evaluation_expr.constant())
    else:
        # TODO: others
        pass

