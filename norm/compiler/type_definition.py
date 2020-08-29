from norm.compiler import NormCompiler, error_on, CodeType
from norm.compiler.expr.compound_expr import compile_compound_expr
from norm.compiler.parsing import parse_type, parse_comments
from norm.executable import TypeDefinition, CodeExecution, NormExecutable
from norm.grammar.normParser import normParser


def _parse_code_block_type(expr: normParser.CodeExprContext) -> CodeType:
    if not expr:
        return CodeType.NORM

    if expr.CODE_BLOCK_BEGIN().getText().lower().find('sql'):
        return CodeType.SQL

    return CodeType.PYTHON


def compile_type_definition(compiler: NormCompiler, atomic: bool, type_definition: normParser.TypeDefinitionContext,
                            comments: str) -> NormExecutable:
    from norm.models.norm import Lambda
    type_variable: Lambda
    type_level: int
    type_declaration: normParser.TypeDeclarationContext = type_definition.typeDeclaration()
    if type_declaration:
        expr = type_definition.compoundExpr().codeExpr()
        code_type = _parse_code_block_type(expr)
        from norm.compiler.type_declaration import compile_type_declaration
        type_variable = compile_type_declaration(compiler, atomic, type_declaration, comments, code_type)
        if code_type != CodeType.NORM:
            return CodeExecution(compiler,
                                 type_=type_variable,
                                 code=expr.children[1].getText())
    else:
        type_: normParser.Type_Context = type_definition.type_()
        type_variable, type_level = parse_type(type_, compiler)
        error_on(type_level > 0, 'Can only define a named first order type.')

    type_variable.atomic = atomic
    type_variable.description = parse_comments(type_variable.name, comments)

    definition_operator: normParser.DefinitionOperatorContext = type_definition.definitionOperator()
    if definition_operator.DEF():
        compound_expr: normParser.CompoundExprContext = type_definition.compoundExpr()
        exec_compound_expr = compile_compound_expr(compiler, compound_expr)
        return TypeDefinition(compiler,
                              dependents=[exec_compound_expr],
                              type_=type_variable)
    else:
        # TODO
        raise NotImplementedError


