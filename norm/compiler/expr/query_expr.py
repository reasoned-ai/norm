from norm.compiler import NormCompiler
from norm.compiler.expr.arguement_expr import compile_arguments
from norm.compiler.parsing import parse_type
from norm.executable import NormExecutable, Query, Argument, AtomicEvaluation, Construction
from norm.parser.normParser import normParser
from typing import Optional


def compile_query_expr(compiler: NormCompiler,
                       query_expr: normParser.QueryExprContext
                       ) -> Optional[NormExecutable]:
    lam, level = parse_type(query_expr.type_(), compiler)
    assert(level == 0)
    arguments = None
    if query_expr.argumentExprs():
        arguments = compile_arguments(compiler, query_expr.argumentExprs())

    if lam.atomic:
        return AtomicEvaluation(context=compiler, dependents=arguments, type_=lam)

    arg: Argument
    is_query = query_expr.QUERY() or any(arg.is_query for arg in arguments.stack)
    if is_query:
        return Query(context=compiler, dependents=arguments, type_=lam)
    else:
        return Construction(context=compiler, dependents=arguments, type_=lam)

