// Generated from /home/ax/Workspace/norm/build/lib/norm/grammar/norm.g4 by ANTLR 4.7.2
package .;
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link normParser}.
 */
public interface normListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link normParser#script}.
	 * @param ctx the parse tree
	 */
	void enterScript(normParser.ScriptContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#script}.
	 * @param ctx the parse tree
	 */
	void exitScript(normParser.ScriptContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#statement}.
	 * @param ctx the parse tree
	 */
	void enterStatement(normParser.StatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#statement}.
	 * @param ctx the parse tree
	 */
	void exitStatement(normParser.StatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#comments}.
	 * @param ctx the parse tree
	 */
	void enterComments(normParser.CommentsContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#comments}.
	 * @param ctx the parse tree
	 */
	void exitComments(normParser.CommentsContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#exports}.
	 * @param ctx the parse tree
	 */
	void enterExports(normParser.ExportsContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#exports}.
	 * @param ctx the parse tree
	 */
	void exitExports(normParser.ExportsContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#imports}.
	 * @param ctx the parse tree
	 */
	void enterImports(normParser.ImportsContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#imports}.
	 * @param ctx the parse tree
	 */
	void exitImports(normParser.ImportsContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#commands}.
	 * @param ctx the parse tree
	 */
	void enterCommands(normParser.CommandsContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#commands}.
	 * @param ctx the parse tree
	 */
	void exitCommands(normParser.CommandsContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#argumentDeclaration}.
	 * @param ctx the parse tree
	 */
	void enterArgumentDeclaration(normParser.ArgumentDeclarationContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#argumentDeclaration}.
	 * @param ctx the parse tree
	 */
	void exitArgumentDeclaration(normParser.ArgumentDeclarationContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#argumentDeclarations}.
	 * @param ctx the parse tree
	 */
	void enterArgumentDeclarations(normParser.ArgumentDeclarationsContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#argumentDeclarations}.
	 * @param ctx the parse tree
	 */
	void exitArgumentDeclarations(normParser.ArgumentDeclarationsContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#rename}.
	 * @param ctx the parse tree
	 */
	void enterRename(normParser.RenameContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#rename}.
	 * @param ctx the parse tree
	 */
	void exitRename(normParser.RenameContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#renames}.
	 * @param ctx the parse tree
	 */
	void enterRenames(normParser.RenamesContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#renames}.
	 * @param ctx the parse tree
	 */
	void exitRenames(normParser.RenamesContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#typeDeclaration}.
	 * @param ctx the parse tree
	 */
	void enterTypeDeclaration(normParser.TypeDeclarationContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#typeDeclaration}.
	 * @param ctx the parse tree
	 */
	void exitTypeDeclaration(normParser.TypeDeclarationContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#version}.
	 * @param ctx the parse tree
	 */
	void enterVersion(normParser.VersionContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#version}.
	 * @param ctx the parse tree
	 */
	void exitVersion(normParser.VersionContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#typeName}.
	 * @param ctx the parse tree
	 */
	void enterTypeName(normParser.TypeNameContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#typeName}.
	 * @param ctx the parse tree
	 */
	void exitTypeName(normParser.TypeNameContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#variable}.
	 * @param ctx the parse tree
	 */
	void enterVariable(normParser.VariableContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#variable}.
	 * @param ctx the parse tree
	 */
	void exitVariable(normParser.VariableContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#queryProjection}.
	 * @param ctx the parse tree
	 */
	void enterQueryProjection(normParser.QueryProjectionContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#queryProjection}.
	 * @param ctx the parse tree
	 */
	void exitQueryProjection(normParser.QueryProjectionContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#constant}.
	 * @param ctx the parse tree
	 */
	void enterConstant(normParser.ConstantContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#constant}.
	 * @param ctx the parse tree
	 */
	void exitConstant(normParser.ConstantContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#code}.
	 * @param ctx the parse tree
	 */
	void enterCode(normParser.CodeContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#code}.
	 * @param ctx the parse tree
	 */
	void exitCode(normParser.CodeContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#codeExpression}.
	 * @param ctx the parse tree
	 */
	void enterCodeExpression(normParser.CodeExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#codeExpression}.
	 * @param ctx the parse tree
	 */
	void exitCodeExpression(normParser.CodeExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#argumentExpression}.
	 * @param ctx the parse tree
	 */
	void enterArgumentExpression(normParser.ArgumentExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#argumentExpression}.
	 * @param ctx the parse tree
	 */
	void exitArgumentExpression(normParser.ArgumentExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#argumentExpressions}.
	 * @param ctx the parse tree
	 */
	void enterArgumentExpressions(normParser.ArgumentExpressionsContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#argumentExpressions}.
	 * @param ctx the parse tree
	 */
	void exitArgumentExpressions(normParser.ArgumentExpressionsContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#evaluationExpression}.
	 * @param ctx the parse tree
	 */
	void enterEvaluationExpression(normParser.EvaluationExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#evaluationExpression}.
	 * @param ctx the parse tree
	 */
	void exitEvaluationExpression(normParser.EvaluationExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#slicedExpression}.
	 * @param ctx the parse tree
	 */
	void enterSlicedExpression(normParser.SlicedExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#slicedExpression}.
	 * @param ctx the parse tree
	 */
	void exitSlicedExpression(normParser.SlicedExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#arithmeticExpression}.
	 * @param ctx the parse tree
	 */
	void enterArithmeticExpression(normParser.ArithmeticExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#arithmeticExpression}.
	 * @param ctx the parse tree
	 */
	void exitArithmeticExpression(normParser.ArithmeticExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#conditionExpression}.
	 * @param ctx the parse tree
	 */
	void enterConditionExpression(normParser.ConditionExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#conditionExpression}.
	 * @param ctx the parse tree
	 */
	void exitConditionExpression(normParser.ConditionExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#oneLineExpression}.
	 * @param ctx the parse tree
	 */
	void enterOneLineExpression(normParser.OneLineExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#oneLineExpression}.
	 * @param ctx the parse tree
	 */
	void exitOneLineExpression(normParser.OneLineExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#multiLineExpression}.
	 * @param ctx the parse tree
	 */
	void enterMultiLineExpression(normParser.MultiLineExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#multiLineExpression}.
	 * @param ctx the parse tree
	 */
	void exitMultiLineExpression(normParser.MultiLineExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#none}.
	 * @param ctx the parse tree
	 */
	void enterNone(normParser.NoneContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#none}.
	 * @param ctx the parse tree
	 */
	void exitNone(normParser.NoneContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#bool_c}.
	 * @param ctx the parse tree
	 */
	void enterBool_c(normParser.Bool_cContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#bool_c}.
	 * @param ctx the parse tree
	 */
	void exitBool_c(normParser.Bool_cContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#integer_c}.
	 * @param ctx the parse tree
	 */
	void enterInteger_c(normParser.Integer_cContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#integer_c}.
	 * @param ctx the parse tree
	 */
	void exitInteger_c(normParser.Integer_cContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#float_c}.
	 * @param ctx the parse tree
	 */
	void enterFloat_c(normParser.Float_cContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#float_c}.
	 * @param ctx the parse tree
	 */
	void exitFloat_c(normParser.Float_cContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#string_c}.
	 * @param ctx the parse tree
	 */
	void enterString_c(normParser.String_cContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#string_c}.
	 * @param ctx the parse tree
	 */
	void exitString_c(normParser.String_cContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#pattern}.
	 * @param ctx the parse tree
	 */
	void enterPattern(normParser.PatternContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#pattern}.
	 * @param ctx the parse tree
	 */
	void exitPattern(normParser.PatternContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#uuid}.
	 * @param ctx the parse tree
	 */
	void enterUuid(normParser.UuidContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#uuid}.
	 * @param ctx the parse tree
	 */
	void exitUuid(normParser.UuidContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#url}.
	 * @param ctx the parse tree
	 */
	void enterUrl(normParser.UrlContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#url}.
	 * @param ctx the parse tree
	 */
	void exitUrl(normParser.UrlContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#datetime}.
	 * @param ctx the parse tree
	 */
	void enterDatetime(normParser.DatetimeContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#datetime}.
	 * @param ctx the parse tree
	 */
	void exitDatetime(normParser.DatetimeContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#logicalOperator}.
	 * @param ctx the parse tree
	 */
	void enterLogicalOperator(normParser.LogicalOperatorContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#logicalOperator}.
	 * @param ctx the parse tree
	 */
	void exitLogicalOperator(normParser.LogicalOperatorContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#spacedLogicalOperator}.
	 * @param ctx the parse tree
	 */
	void enterSpacedLogicalOperator(normParser.SpacedLogicalOperatorContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#spacedLogicalOperator}.
	 * @param ctx the parse tree
	 */
	void exitSpacedLogicalOperator(normParser.SpacedLogicalOperatorContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#newlineLogicalOperator}.
	 * @param ctx the parse tree
	 */
	void enterNewlineLogicalOperator(normParser.NewlineLogicalOperatorContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#newlineLogicalOperator}.
	 * @param ctx the parse tree
	 */
	void exitNewlineLogicalOperator(normParser.NewlineLogicalOperatorContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#conditionOperator}.
	 * @param ctx the parse tree
	 */
	void enterConditionOperator(normParser.ConditionOperatorContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#conditionOperator}.
	 * @param ctx the parse tree
	 */
	void exitConditionOperator(normParser.ConditionOperatorContext ctx);
	/**
	 * Enter a parse tree produced by {@link normParser#spacedConditionOperator}.
	 * @param ctx the parse tree
	 */
	void enterSpacedConditionOperator(normParser.SpacedConditionOperatorContext ctx);
	/**
	 * Exit a parse tree produced by {@link normParser#spacedConditionOperator}.
	 * @param ctx the parse tree
	 */
	void exitSpacedConditionOperator(normParser.SpacedConditionOperatorContext ctx);
}