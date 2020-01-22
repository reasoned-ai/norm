from norm.compiler import NormCompiler
from norm.compiler.expr import random_output_variable, Var
from norm.compiler.expr.assignment_expr import compile_assignment_expr
from norm.executable import NormExecutable
from norm.executable import Return
from norm.grammar.normParser import normParser


def compile_return(compiler, return_expr):
    """
    Compile return expression
    :type compiler: NormCompiler
    :type return_expr: normParser.ReturnExprContext
    :rtype: NormExecutable
    """
    if return_expr.IS() or return_expr.AS():
        dependents = [compile_assignment_expr(compiler, simple_expr, Var(v.getText()))
                      for v, simple_expr in zip(return_expr.getTypedRuleContexts(normParser.VariableContext),
                                                return_expr.getTypedRuleContexts(normParser.SimpleExprContext))]
    else:
        dependents = [compile_assignment_expr(compiler, simple_expr, random_output_variable())
                      for simple_expr in return_expr.getTypedRuleContexts(normParser.SimpleExprContext)]
    return Return(compiler, dependents=dependents)


