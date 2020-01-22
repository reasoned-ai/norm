from norm.compiler import NormCompiler
from norm.compiler.expr import Var
from norm.compiler.expr.assignment_expr import compile_assignment_expr
from norm.compiler.expr.code_expr import compile_code_expr
from norm.compiler.expr.conjunction_expr import compile_conjunction
from norm.compiler.expr.disjunction_expr import compile_disjunction
from norm.compiler.expr.except_expr import compile_except
from norm.compiler.expr.implication_expr import compile_implication_expr
from norm.compiler.expr.mutual_exclusion_expr import compile_mutual_exclusive
from norm.compiler.expr.negation_expr import compile_negation_expr
from norm.compiler.expr.random_generation_expr import compile_random_generation_expr
from norm.compiler.expr.return_expr import compile_return
from norm.compiler.expr.simple_expr import compile_simple_expr
from norm.compiler.expr.switch_block import compile_switch_block
from norm.compiler.expr.quantified_expr import compile_quantifier_expr
from norm.executable import NormExecutable
from norm.grammar.normParser import normParser


def compile_compound_expr(compiler, compound_expr):
    """
    :type compiler: NormCompiler
    :type compound_expr: normParser.CompoundExprContext
    :rtype: NormExecutable
    """
    if compound_expr.simpleExpr():
        return compile_simple_expr(compiler, compound_expr.simpleExpr())
    elif compound_expr.codeExpr():
        return compile_code_expr(compiler, compound_expr.codeExpr())
    elif compound_expr.returnExpr():
        return compile_return(compiler, compound_expr.returnExpr())
    elif compound_expr.quantifier():
        return compile_quantifier_expr(compiler, compound_expr.quantifier(), compound_expr.names(),
                                       compound_expr.simpleExpr(), compound_expr.compoundExpr())
    elif compound_expr.IS() or compound_expr.AS():
        variables = [Var(v.getText()) for v in compound_expr.getTypedRuleContexts(normParser.VariableContext)]
        return compile_assignment_expr(compiler, compound_expr.compoundExpr(), variables)
    elif compound_expr.DRAW():
        variables = [Var(v.getText()) for v in compound_expr.getTypedRuleContexts(normParser.VariableContext)]
        return compile_random_generation_expr(compiler, compound_expr.compoundExpr(), variables)
    elif compound_expr.NOT():
        return compile_negation_expr(compiler, compound_expr.compoundExpr())
    elif compound_expr.complexLogicalOperator():
        left_expr = compound_expr.compoundExpr(0)
        right_expr = compound_expr.compoundExpr(1)
        operator: normParser.ComplexLogicalOperatorContext = compound_expr.complexLogicalOperator()
        if operator.IMP():
            return compile_implication_expr(compiler, left_expr, right_expr)
        elif operator.EPT():
            return compile_except(compiler, left_expr, right_expr)
    elif compound_expr.simpleLogicalOperator():
        left_expr = compound_expr.compoundExpr(0)
        right_expr = compound_expr.compoundExpr(1)
        operator: normParser.SimpleLogicalOperatorContext = compound_expr.simpleLogicalOperator()
        if operator.AND():
            return compile_conjunction(compiler, left_expr, right_expr)
        elif operator.OR():
            return compile_disjunction(compiler, left_expr, right_expr)
        elif operator.XOR():
            return compile_mutual_exclusive(compiler, left_expr, right_expr)
        elif operator.OTW():
            return compile_switch_block(compiler, left_expr, right_expr)





