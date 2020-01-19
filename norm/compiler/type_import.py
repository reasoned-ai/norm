from typing import List
from norm.compiler import NormCompilable
from norm.grammar.normParser import normParser


class TypeImport(NormCompilable):

    def compile(self, atomic, type_import, comments):
        """
        :type atomic: bool
        :type type_import: normParser.TypeImportContext
        :type comments: str
        :rtype: List[NormExecutable]
        """
        pass


