from typing import List
from norm.compiler import NormCompilable, Variable
from norm.compiler.constants import OUTPUT_VAR_STUB, TEMP_VAR_STUB
from norm.compiler.expr.code_expr import CodeExpr
from norm.compiler.expr.implication_expr import ImplicationExpr
from norm.compiler.expr.negation_expr import NegationExpr
from norm.compiler.expr.random_generation_expr import RandomGenerationExpr
from norm.compiler.expr.simple_expr import SimpleExpr
from norm.compiler.expr.assignment_expr import AssignmentExpr
from norm.compiler.parsing import parse_variable
from norm.executable import Return, Difference
from norm.grammar.normParser import normParser


class CompoundExpr(NormCompilable):

    def compile_return(self, return_expr):
        """
        Compile return expression
        :type return_expr: normParser.ReturnExprContext
        :rtype: List[norm.executable.NormExecutable]
        """
        exe = Return(self.compiler)
        ae = AssignmentExpr(self.compiler)
        if return_expr.IS() or return_expr.AS():
            for v, simple_expr in zip(return_expr.getTypedRuleContexts(normParser.VariableContext),
                                      return_expr.getTypedRuleContexts(normParser.SimpleExprContext)):
                exe.push(ae.compile(simple_expr, [parse_variable(v)]))
        else:
            for i, simple_expr in enumerate(return_expr.getTypedRuleContexts(normParser.SimpleExprContext)):
                exe.push(ae.compile(simple_expr, [Variable(OUTPUT_VAR_STUB + str(i))]))
        return [exe]

    def compile_except(self, left_expr, right_expr):
        ae = AssignmentExpr

    def compile(self, compound_expr):
        """
        :type compound_expr: normParser.CompoundExprContext
        :rtype: List[norm.executable.NormExecutable]
        """
        if compound_expr.simpleExpr():
            return SimpleExpr(self.compiler).compile(compound_expr.simpleExpr())
        elif compound_expr.codeExpr():
            return CodeExpr(self.compiler).compile(compound_expr.codeExpr())
        elif compound_expr.returnExpr():
            return self.compile_return(compound_expr.returnExpr())
        elif compound_expr.quantifier():
            pass
        elif compound_expr.IS() or compound_expr.AS():
            variables = [parse_variable(v) for v in compound_expr.getTypedRuleContexts(normParser.VariableContext)]
            return [AssignmentExpr(self.compiler).compile(compound_expr.compoundExpr(), variables)]
        elif compound_expr.DRAW():
            variables = [parse_variable(v) for v in compound_expr.getTypedRuleContexts(normParser.VariableContext)]
            return RandomGenerationExpr(self.compiler).compile(compound_expr.compoundExpr(), variables)
        elif compound_expr.NOT():
            return NegationExpr(self.compiler).compile(compound_expr.compoundExpr())
        elif compound_expr.complexLogicalOperator():
            operator: normParser.ComplexLogicalOperatorContext = compound_expr.complexLogicalOperator()
            if operator.IMP():
                return ImplicationExpr(self.compiler).compile(compound_expr.compoundExpr(0),
                                                              compound_expr.compoundExpr(1))
            elif operator.EPT():
                exe1 = AssignmentExpr(self.compiler).compile(compound_expr.compoundExpr(0),
                                                             [Variable(TEMP_VAR_STUB + '0')])
                exe2 = AssignmentExpr(self.compiler).compile(compound_expr.compoundExpr(1),
                                                             [Variable(TEMP_VAR_STUB + '1')])
                exe = Difference(self.compiler)
                exe.push(exe1)
                exe.push(exe2)
                return [exe]
            elif operator.OTW():



