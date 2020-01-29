from typing import List

from antlr4 import ParserRuleContext

from norm.compiler import NormCompiler, CodeType
from norm.compiler.expr import TEMP_VAR_STUB
from norm.compiler.expr.compound_expr import compile_compound_expr
from norm.compiler.type_declaration import compile_type_declaration
from norm.compiler.type_definition import compile_type_definition, _parse_code_block_type
from norm.compiler.type_export import compile_type_export
from norm.compiler.type_import import compile_type_import
from norm.executable import NormExecutable, DefineType, CodeExecution
from norm.grammar.normParser import normParser
from norm.utils import random_name


def _unroll_array(compiler, ctx_s, ctx_t, t, comments, atomic):
    """
    Unroll the array of contexts
    :type compiler: NormCompiler
    :type ctx_s: ParserRuleContext
    :type ctx_t: type
    :type t: Callable[[NormCompiler, bool, ParserRuleContext, str], NormExecutable]
    :type comments: str
    :type atomic: bool
    :rtype: NormExecutable
    """
    if not ctx_s:
        return []

    exes = []
    for a in ctx_s.getTypedRuleContexts(ctx_t):
        exe = t(compiler, atomic, a, comments)
        if isinstance(exe, NormExecutable):
            exes.append(exe)
    return NormExecutable(compiler, dependents=exes)


def compile_statement(compiler, comments, statement):
    """
    :type compiler: norm.compiler.NormCompiler
    :type comments: str
    :type statement: normParser.StatementContext
    :rtype: NormExecutable
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
        random_type_variable = compiler.get_lambda(TEMP_VAR_STUB + random_name(),
                                                   module=compiler.current_module,
                                                   code_type=code_type)
        if code_type != CodeType.NORM:
            return CodeExecution(compiler,
                                 type_=random_type_variable,
                                 code=expr.children[1].getText())
        else:
            return DefineType(compiler,
                              dependents=[compile_compound_expr(compiler, statement.compoundExpr())],
                              type_=random_type_variable)


