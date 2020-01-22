from norm.compiler import NormCompiler, error_on
from norm.compiler.expr.compound_expr import compile_compound_expr
from norm.compiler.parsing import parse_type, parse_comments
from norm.compiler.type_declaration import compile_type_declaration
from norm.executable import DefineType
from norm.grammar.normParser import normParser


def compile_new_definition(compiler, type_variable, compound_expr):
    """
    :type compiler: NormCompiler
    :type type_variable: norm.models.norm.Lambda
    :type compound_expr: normParser.CompoundExprContext
    :rtype: norm.executable.NormExecutable
    """
    exe = DefineType(compiler, dependents=[compile_compound_expr(compiler, compound_expr)])
    exe.lam = type_variable
    return exe


def compile_type_definition(compiler, atomic, type_definition, comments):
    """
    :type compiler: NormCompiler
    :type atomic: bool
    :type type_definition: normParser.TypeDefinitionContext
    :type comments: str
    :rtype: norm.executable.NormExecutable
    """
    from norm.models.norm import Lambda
    variable_type: Lambda
    type_level: int
    type_declaration: normParser.TypeDeclarationContext = type_definition.typeDeclaration()
    if type_declaration:
        type_variable = compile_type_declaration(compiler, atomic, type_declaration, comments)
    else:
        type_: normParser.Type_Context = type_definition.type_()
        type_variable, type_level = parse_type(type_, compiler)
        error_on(type_level > 0, 'Can only define a named type. Not an anonymous higher-order type.')
    type_variable.atomic = atomic
    type_variable.description = parse_comments(type_variable.name, comments)

    definition_operator: normParser.DefinitionOperatorContext = type_definition.definitionOperator()
    if definition_operator.DEF():
        return compile_new_definition(compiler, type_variable, type_definition.compoundExpr())
    else:
        # TODO
        raise NotImplementedError


