from typing import List, Type, Callable
from norm.utils import random_name
from norm.compiler import NormCompiler
from norm.compiler.expr import TEMP_VAR_STUB
from norm.compiler.type_import import compile_type_import
from norm.compiler.type_export import compile_type_export
from norm.compiler.type_declaration import compile_type_declaration
from norm.compiler.type_definition import compile_type_definition, compile_new_definition
from norm.executable import NormExecutable
from norm.grammar.normParser import normParser
from antlr4 import ParserRuleContext


def _unroll_atomic_array(compiler, ctx_s, ctx_t, t, comments):
    """
    Unroll the array of contexts
    :type compiler: NormCompiler
    :type ctx_s: ParserRuleContext
    :type ctx_t: type
    :type t: Callable[[NormCompiler, bool, ParserRuleContext, str], NormExecutable]
    :type comments: str
    :rtype: List[NormExecutable]
    """
    if not ctx_s:
        return []

    exes = []
    atomic = False
    for a in ctx_s.children:
        if isinstance(a, normParser.ATOMIC):
            atomic = True
        elif isinstance(a, ctx_t):
            exe = t(compiler, atomic, a, comments)
            if isinstance(exe, NormExecutable):
                exes.append(exe)
            atomic = False
    return exes


def compile_statement(compiler, comments, statement):
    """
    :type compiler: norm.compiler.NormCompiler
    :type comments: str
    :type statement: normParser.StatementContext
    :rtype: List[NormExecutable]
    """
    if statement.typeImports():
        exes = _unroll_atomic_array(compiler,
                                    statement.typeImports(),
                                    normParser.TypeImportContext,
                                    compile_type_import,
                                    comments)
    elif statement.typeExports():
        exes = _unroll_atomic_array(compiler,
                                    statement.typeExports(),
                                    normParser.TypeExportContext,
                                    compile_type_export,
                                    comments)
    elif statement.typeDeclarations():
        exes = _unroll_atomic_array(compiler,
                                    statement.typeDeclarations(),
                                    normParser.TypeDeclarationContext,
                                    compile_type_declaration,
                                    comments)
    elif statement.typeDefinitions():
        exes = _unroll_atomic_array(compiler,
                                    statement.typeDefinitions(),
                                    normParser.TypeDefinitionContext,
                                    compile_type_definition,
                                    comments)
    else:
        random_type_variable = compiler.get_lambda(TEMP_VAR_STUB + random_name())
        exes = [compile_new_definition(compiler, random_type_variable, statement.compoundExpr())]
    return exes


