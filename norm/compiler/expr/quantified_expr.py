from norm.compiler import NormCompiler
from norm.executable import NormExecutable
from norm.grammar.normParser import normParser


def compile_quantifier_expr(compiler, quantifier, variables, domain, expr):
    """
    Compile quantified expressions
    :type compiler: NormCompiler
    :type quantifier: normParser.QuantifierContext
    :type variables: normParser.NamesContext
    :type domain: normParser.SimpleExprContext
    :type expr: normParser.CompoundExprContext
    :rtype: NormExecutable
    """
    pass


