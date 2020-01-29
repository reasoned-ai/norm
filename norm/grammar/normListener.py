# Generated from /home/ax/Workspace/norm/norm/grammar/norm.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .normParser import normParser
else:
    from normParser import normParser

# This class defines a complete listener for a parse tree produced by normParser.
class normListener(ParseTreeListener):

    # Enter a parse tree produced by normParser#module.
    def enterModule(self, ctx:normParser.ModuleContext):
        pass

    # Exit a parse tree produced by normParser#module.
    def exitModule(self, ctx:normParser.ModuleContext):
        pass


    # Enter a parse tree produced by normParser#full_statement.
    def enterFull_statement(self, ctx:normParser.Full_statementContext):
        pass

    # Exit a parse tree produced by normParser#full_statement.
    def exitFull_statement(self, ctx:normParser.Full_statementContext):
        pass


    # Enter a parse tree produced by normParser#comments.
    def enterComments(self, ctx:normParser.CommentsContext):
        pass

    # Exit a parse tree produced by normParser#comments.
    def exitComments(self, ctx:normParser.CommentsContext):
        pass


    # Enter a parse tree produced by normParser#statement.
    def enterStatement(self, ctx:normParser.StatementContext):
        pass

    # Exit a parse tree produced by normParser#statement.
    def exitStatement(self, ctx:normParser.StatementContext):
        pass


    # Enter a parse tree produced by normParser#validName.
    def enterValidName(self, ctx:normParser.ValidNameContext):
        pass

    # Exit a parse tree produced by normParser#validName.
    def exitValidName(self, ctx:normParser.ValidNameContext):
        pass


    # Enter a parse tree produced by normParser#qualifiedName.
    def enterQualifiedName(self, ctx:normParser.QualifiedNameContext):
        pass

    # Exit a parse tree produced by normParser#qualifiedName.
    def exitQualifiedName(self, ctx:normParser.QualifiedNameContext):
        pass


    # Enter a parse tree produced by normParser#type_.
    def enterType_(self, ctx:normParser.Type_Context):
        pass

    # Exit a parse tree produced by normParser#type_.
    def exitType_(self, ctx:normParser.Type_Context):
        pass


    # Enter a parse tree produced by normParser#variable.
    def enterVariable(self, ctx:normParser.VariableContext):
        pass

    # Exit a parse tree produced by normParser#variable.
    def exitVariable(self, ctx:normParser.VariableContext):
        pass


    # Enter a parse tree produced by normParser#names.
    def enterNames(self, ctx:normParser.NamesContext):
        pass

    # Exit a parse tree produced by normParser#names.
    def exitNames(self, ctx:normParser.NamesContext):
        pass


    # Enter a parse tree produced by normParser#typeImport.
    def enterTypeImport(self, ctx:normParser.TypeImportContext):
        pass

    # Exit a parse tree produced by normParser#typeImport.
    def exitTypeImport(self, ctx:normParser.TypeImportContext):
        pass


    # Enter a parse tree produced by normParser#typeImports.
    def enterTypeImports(self, ctx:normParser.TypeImportsContext):
        pass

    # Exit a parse tree produced by normParser#typeImports.
    def exitTypeImports(self, ctx:normParser.TypeImportsContext):
        pass


    # Enter a parse tree produced by normParser#typeExport.
    def enterTypeExport(self, ctx:normParser.TypeExportContext):
        pass

    # Exit a parse tree produced by normParser#typeExport.
    def exitTypeExport(self, ctx:normParser.TypeExportContext):
        pass


    # Enter a parse tree produced by normParser#typeExports.
    def enterTypeExports(self, ctx:normParser.TypeExportsContext):
        pass

    # Exit a parse tree produced by normParser#typeExports.
    def exitTypeExports(self, ctx:normParser.TypeExportsContext):
        pass


    # Enter a parse tree produced by normParser#variableDeclaration.
    def enterVariableDeclaration(self, ctx:normParser.VariableDeclarationContext):
        pass

    # Exit a parse tree produced by normParser#variableDeclaration.
    def exitVariableDeclaration(self, ctx:normParser.VariableDeclarationContext):
        pass


    # Enter a parse tree produced by normParser#inputDeclaration.
    def enterInputDeclaration(self, ctx:normParser.InputDeclarationContext):
        pass

    # Exit a parse tree produced by normParser#inputDeclaration.
    def exitInputDeclaration(self, ctx:normParser.InputDeclarationContext):
        pass


    # Enter a parse tree produced by normParser#outputDeclaration.
    def enterOutputDeclaration(self, ctx:normParser.OutputDeclarationContext):
        pass

    # Exit a parse tree produced by normParser#outputDeclaration.
    def exitOutputDeclaration(self, ctx:normParser.OutputDeclarationContext):
        pass


    # Enter a parse tree produced by normParser#typeDeclaration.
    def enterTypeDeclaration(self, ctx:normParser.TypeDeclarationContext):
        pass

    # Exit a parse tree produced by normParser#typeDeclaration.
    def exitTypeDeclaration(self, ctx:normParser.TypeDeclarationContext):
        pass


    # Enter a parse tree produced by normParser#typeDeclarations.
    def enterTypeDeclarations(self, ctx:normParser.TypeDeclarationsContext):
        pass

    # Exit a parse tree produced by normParser#typeDeclarations.
    def exitTypeDeclarations(self, ctx:normParser.TypeDeclarationsContext):
        pass


    # Enter a parse tree produced by normParser#typeDefinition.
    def enterTypeDefinition(self, ctx:normParser.TypeDefinitionContext):
        pass

    # Exit a parse tree produced by normParser#typeDefinition.
    def exitTypeDefinition(self, ctx:normParser.TypeDefinitionContext):
        pass


    # Enter a parse tree produced by normParser#argumentExpr.
    def enterArgumentExpr(self, ctx:normParser.ArgumentExprContext):
        pass

    # Exit a parse tree produced by normParser#argumentExpr.
    def exitArgumentExpr(self, ctx:normParser.ArgumentExprContext):
        pass


    # Enter a parse tree produced by normParser#argumentExprs.
    def enterArgumentExprs(self, ctx:normParser.ArgumentExprsContext):
        pass

    # Exit a parse tree produced by normParser#argumentExprs.
    def exitArgumentExprs(self, ctx:normParser.ArgumentExprsContext):
        pass


    # Enter a parse tree produced by normParser#queryExpr.
    def enterQueryExpr(self, ctx:normParser.QueryExprContext):
        pass

    # Exit a parse tree produced by normParser#queryExpr.
    def exitQueryExpr(self, ctx:normParser.QueryExprContext):
        pass


    # Enter a parse tree produced by normParser#rangeExpr.
    def enterRangeExpr(self, ctx:normParser.RangeExprContext):
        pass

    # Exit a parse tree produced by normParser#rangeExpr.
    def exitRangeExpr(self, ctx:normParser.RangeExprContext):
        pass


    # Enter a parse tree produced by normParser#evaluationExpr.
    def enterEvaluationExpr(self, ctx:normParser.EvaluationExprContext):
        pass

    # Exit a parse tree produced by normParser#evaluationExpr.
    def exitEvaluationExpr(self, ctx:normParser.EvaluationExprContext):
        pass


    # Enter a parse tree produced by normParser#arithmeticExpr.
    def enterArithmeticExpr(self, ctx:normParser.ArithmeticExprContext):
        pass

    # Exit a parse tree produced by normParser#arithmeticExpr.
    def exitArithmeticExpr(self, ctx:normParser.ArithmeticExprContext):
        pass


    # Enter a parse tree produced by normParser#simpleExpr.
    def enterSimpleExpr(self, ctx:normParser.SimpleExprContext):
        pass

    # Exit a parse tree produced by normParser#simpleExpr.
    def exitSimpleExpr(self, ctx:normParser.SimpleExprContext):
        pass


    # Enter a parse tree produced by normParser#codeExpr.
    def enterCodeExpr(self, ctx:normParser.CodeExprContext):
        pass

    # Exit a parse tree produced by normParser#codeExpr.
    def exitCodeExpr(self, ctx:normParser.CodeExprContext):
        pass


    # Enter a parse tree produced by normParser#returnExpr.
    def enterReturnExpr(self, ctx:normParser.ReturnExprContext):
        pass

    # Exit a parse tree produced by normParser#returnExpr.
    def exitReturnExpr(self, ctx:normParser.ReturnExprContext):
        pass


    # Enter a parse tree produced by normParser#compoundExpr.
    def enterCompoundExpr(self, ctx:normParser.CompoundExprContext):
        pass

    # Exit a parse tree produced by normParser#compoundExpr.
    def exitCompoundExpr(self, ctx:normParser.CompoundExprContext):
        pass


    # Enter a parse tree produced by normParser#constant.
    def enterConstant(self, ctx:normParser.ConstantContext):
        pass

    # Exit a parse tree produced by normParser#constant.
    def exitConstant(self, ctx:normParser.ConstantContext):
        pass


    # Enter a parse tree produced by normParser#measurement.
    def enterMeasurement(self, ctx:normParser.MeasurementContext):
        pass

    # Exit a parse tree produced by normParser#measurement.
    def exitMeasurement(self, ctx:normParser.MeasurementContext):
        pass


    # Enter a parse tree produced by normParser#scalar.
    def enterScalar(self, ctx:normParser.ScalarContext):
        pass

    # Exit a parse tree produced by normParser#scalar.
    def exitScalar(self, ctx:normParser.ScalarContext):
        pass


    # Enter a parse tree produced by normParser#string.
    def enterString(self, ctx:normParser.StringContext):
        pass

    # Exit a parse tree produced by normParser#string.
    def exitString(self, ctx:normParser.StringContext):
        pass


    # Enter a parse tree produced by normParser#definitionOperator.
    def enterDefinitionOperator(self, ctx:normParser.DefinitionOperatorContext):
        pass

    # Exit a parse tree produced by normParser#definitionOperator.
    def exitDefinitionOperator(self, ctx:normParser.DefinitionOperatorContext):
        pass


    # Enter a parse tree produced by normParser#simpleLogicalOperator.
    def enterSimpleLogicalOperator(self, ctx:normParser.SimpleLogicalOperatorContext):
        pass

    # Exit a parse tree produced by normParser#simpleLogicalOperator.
    def exitSimpleLogicalOperator(self, ctx:normParser.SimpleLogicalOperatorContext):
        pass


    # Enter a parse tree produced by normParser#complexLogicalOperator.
    def enterComplexLogicalOperator(self, ctx:normParser.ComplexLogicalOperatorContext):
        pass

    # Exit a parse tree produced by normParser#complexLogicalOperator.
    def exitComplexLogicalOperator(self, ctx:normParser.ComplexLogicalOperatorContext):
        pass


    # Enter a parse tree produced by normParser#comparisonOperator.
    def enterComparisonOperator(self, ctx:normParser.ComparisonOperatorContext):
        pass

    # Exit a parse tree produced by normParser#comparisonOperator.
    def exitComparisonOperator(self, ctx:normParser.ComparisonOperatorContext):
        pass


    # Enter a parse tree produced by normParser#quantifier.
    def enterQuantifier(self, ctx:normParser.QuantifierContext):
        pass

    # Exit a parse tree produced by normParser#quantifier.
    def exitQuantifier(self, ctx:normParser.QuantifierContext):
        pass



del normParser