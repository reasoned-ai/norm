from typing import List
from norm.compiler import NormCompilable
from norm.compiler.type_import import TypeImport
from norm.compiler.type_export import TypeExport
from norm.compiler.type_declaration import TypeDeclaration
from norm.compiler.type_definition import TypeDefinition
from norm.compiler.expr.compound_expr import CompoundExpr
from norm.executable import NormExecutable
from norm.grammar.normParser import normParser


class Statement(NormCompilable):

    def _unroll_atomic_array(self, array, ctx, t, comments):
        """
        Unroll the array of contexts
        :type array: List[normParser.ParserRuleContext]
        :type ctx: normParser.ParserRuleContext
        :type t: Type[NormCompilable]
        :type comments: str
        :rtype: List[NormExecutable]
        """
        if not array:
            return []

        exes = []
        atomic = False
        ts = t(self)
        for a in array:
            if isinstance(a, normParser.ATOMIC):
                atomic = True
            elif isinstance(a, ctx):
                exes.extend(ts.compile(atomic, a, comments))
                atomic = False
        return exes

    def compile(self, comments, statement):
        """
        :type comments: str
        :type statement: normParser.StatementContext
        :rtype: List[NormExecutable]
        """
        exes = self._unroll_atomic_array(statement.typeImports(),
                                         normParser.TypeImportContext,
                                         TypeImport,
                                         comments)
        exes.extend(self._unroll_atomic_array(statement.typeExports(),
                                              normParser.TypeExportContext,
                                              TypeExport,
                                              comments))
        exes.extend(self._unroll_atomic_array(statement.typeDeclarations(),
                                              normParser.TypeDeclarationContext,
                                              TypeDeclaration,
                                              comments))
        exes.extend(self._unroll_atomic_array(statement.typeDefinitions(),
                                              normParser.TypeDefinitionContext,
                                              TypeDefinition,
                                              comments))
        exes.extend(CompoundExpr(self).compile(statement.compoundExpr()))
        return exes


