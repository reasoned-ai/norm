from norm.compiler import NormCompiler, error_on, CodeType
from norm.compiler.expr.compound_expr import compile_compound_expr
from norm.compiler.parsing import parse_type, parse_comments
from norm.compiler.type_declaration import compile_type_declaration
from norm.executable import DefineType, CodeExecution
from norm.grammar.normParser import normParser


def _parse_code_block_type(expr):
    """
    :type expr: normParser.CodeExprContext
    :rtype: CodeType
    """
    if not expr:
        return CodeType.NORM

    if expr.CODE_BLOCK_BEGIN().getText().find('sql'):
        return CodeType.SQL

    return CodeType.PYTHON


def compile_type_definition(compiler, atomic, type_definition, comments):
    """
    :type compiler: NormCompiler
    :type atomic: bool
    :type type_definition: normParser.TypeDefinitionContext
    :type comments: str
    :rtype: norm.executable.NormExecutable
    """
    from norm.models.norm import Lambda
    type_variable: Lambda
    type_level: int
    type_declaration: normParser.TypeDeclarationContext = type_definition.typeDeclaration()
    if type_declaration:
        expr = type_definition.compoundExpr().codeExpr()
        code_type = _parse_code_block_type(expr)
        type_variable = compile_type_declaration(compiler, atomic, type_declaration, comments, code_type)
        if code_type != CodeType.NORM:
            return CodeExecution(compiler,
                                 type_=type_variable,
                                 code=expr.children[1].getText())
    else:
        type_: normParser.Type_Context = type_definition.type_()
        type_variable, type_level = parse_type(type_, compiler)
        error_on(type_level > 0, 'Can only define a named type. Not an anonymous higher-order type.')

    type_variable.atomic = atomic
    type_variable.description = parse_comments(type_variable.name, comments)

    definition_operator: normParser.DefinitionOperatorContext = type_definition.definitionOperator()
    if definition_operator.DEF():
        compound_expr: normParser.CompoundExprContext = type_definition.compoundExpr()
        return DefineType(compiler,
                          dependents=[compile_compound_expr(compiler, compound_expr)],
                          type_=type_variable)
    else:
        # TODO
        raise NotImplementedError


