from typing import Callable, Optional, Any

from antlr4 import ParserRuleContext

from norm.compiler import NormCompiler, CodeType
from norm.compiler.expr import TEMP_VAR_STUB
from norm.compiler.expr.compound_expr import compile_compound_expr
from norm.compiler.type_declaration import compile_type_declaration
from norm.compiler.type_definition import compile_type_definition, _parse_code_block_type
from norm.compiler.type_export import compile_type_export
from norm.compiler.type_import import compile_type_import
from norm.executable import NormExecutable, TypeDefinition, CodeExecution
from norm.parser.normParser import normParser
from norm.utils import random_name


def _unroll_array(compiler: NormCompiler, ctx_s: ParserRuleContext, ctx_t: type,
                  t: Callable[[NormCompiler, bool, Any, str], Optional[NormExecutable]],
                  comments: str, atomic: bool) -> Optional[NormExecutable]:
    """
    Unroll the array of contexts
    """
    if ctx_s is None:
        return None

    exes = []
    for a in ctx_s.getTypedRuleContexts(ctx_t):
        exe = t(compiler, atomic, a, comments)
        if isinstance(exe, NormExecutable):
            exes.append(exe)
    return NormExecutable(compiler, dependents=exes)


def compile_statement(compiler: NormCompiler, comments: str,
                      statement: normParser.StatementContext) -> Optional[NormExecutable]:
    """
    Compile a single statement
    """
    atomic = statement.ATOMIC() is not None
    if statement.typeImports():
        return _unroll_array(compiler,
                             statement.typeImports(),
                             normParser.TypeImportContext,
                             compile_type_import,
                             comments,
                             atomic)
    elif statement.typeExports():
        return _unroll_array(compiler,
                             statement.typeExports(),
                             normParser.TypeExportContext,
                             compile_type_export,
                             comments,
                             atomic)
    elif statement.typeDeclarations():
        return _unroll_array(compiler,
                             statement.typeDeclarations(),
                             normParser.TypeDeclarationContext,
                             compile_type_declaration,
                             comments,
                             atomic)
    elif statement.typeDefinition():
        return compile_type_definition(compiler, atomic, statement.typeDefinition(), comments)
    else:
        expr: normParser.CodeExprContext = statement.compoundExpr().codeExpr()
        code_type: CodeType = _parse_code_block_type(expr)
        random_type_variable = compiler.create_lambda(name=TEMP_VAR_STUB + random_name(),
                                                      atomic=atomic,
                                                      code_type=code_type)
        if code_type != CodeType.NORM:
            return CodeExecution(compiler,
                                 type_=random_type_variable,
                                 code=expr.children[1].getText())
        else:
            return TypeDefinition(compiler,
                                  dependents=[compile_compound_expr(compiler, statement.compoundExpr())],
                                  type_=random_type_variable)


