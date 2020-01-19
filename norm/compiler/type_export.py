from typing import List
from norm.compiler import NormCompilable
from norm.grammar.normParser import normParser


class TypeExport(NormCompilable):

    def compile(self, atomic, type_export, comments):
        """
        :type atomic: bool
        :type type_export: normParser.TypeExportContext
        :type comments: str
        :rtype: List[NormExecutable]
        """
        pass



