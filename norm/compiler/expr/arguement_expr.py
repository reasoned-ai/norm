from norm.compiler import NormCompiler
from norm.executable import NormExecutable, Argument
from norm.grammar.normParser import normParser
from typing import List


def compile_argument(compiler: NormCompiler,
                     argument: normParser.ArgumentExprContext
                     ) -> Argument:
    if argument.QUERY():
        assert(argument.argumentExpr().QUERY() is None)
        arg = compile_argument(compiler, argument.argumentExpr())
        arg.is_query = True
        return arg
    from norm.compiler.expr.simple_expr import compile_simple_expr
    expr = compile_simple_expr(compiler, argument.simpleExpr())
    variable_name = None
    if argument.IS():
        variable_name = argument.validName().getText()
    arg = Argument(compiler, expr, variable_name)
    return arg


def compile_arguments(compiler: NormCompiler,
                      arguments: normParser.ArgumentExprsContext
                      ) -> List[NormExecutable]:
    args = []
    ch: normParser.ArgumentExprContext
    for ch in arguments.getTypedRuleContexts(normParser.ArgumentExprContext):
        args.append(compile_argument(compiler, ch))

    return args

