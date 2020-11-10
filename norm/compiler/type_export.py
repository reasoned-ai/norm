from norm.executable import NormExecutable
from norm.parser.normParser import normParser
from norm.compiler import NormCompiler
from typing import Optional


def compile_type_export(compiler: NormCompiler, atomic: bool, type_export: normParser.TypeExportContext,
                        comments: str) -> Optional[NormExecutable]:
    pass



