from typing import List

from norm.compiler import NormCompiler, error_on
from norm.compiler.expr import Var
from norm.compiler.expr.compound_expr import compile_compound_expr
from norm.compiler.expr.simple_expr import compile_simple_expr
from norm.executable import NormExecutable, Project, Pivot, Join
from norm.grammar.normParser import normParser


def compile_assignment_expr(compiler, expr, variables):
    """
    Compile assignment expression
    :type compiler: NormCompiler
    :type expr: normParser.CompoundExprContext or normParser.SimpleExprContext
    :type variables: Var or List[Var]
    :rtype: NormExecutable
    """
    exe: NormExecutable or None = None
    if isinstance(expr, normParser.CompoundExprContext):
        exe = compile_compound_expr(compiler, expr)
    elif isinstance(expr, normParser.SimpleExprContext):
        exe = compile_simple_expr(compiler, expr)
    error_on(exe is None, f'Assignment can take either compound or simple expression only. Not {type(expr)}')

    if isinstance(variables, list):
        error_on(any(v.pivot for v in variables),
                 "Only one pivoting variable can be assigned at a time")
        return Project(compiler, dependents=[exe], variables=[v.name for v in variables])
    else:
        v: Var = variables
        if v.pivot:
            if not all(name in exe.lam for name in v.dependents):
                # Join the results with current scope before pivoting
                #  because some dependent variable to compose the pivot is not in the results
                return Pivot(compiler, dependents=[Join(compiler, dependents=[exe])], variable=v.name)
            else:
                return Pivot(compiler, dependents=[exe], variable=v.name)
        else:
            return Project(compiler, dependents=[exe], variables=[v.name])
