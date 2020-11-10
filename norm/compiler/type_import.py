from norm.executable import NormExecutable
from norm.parser.normParser import normParser
from norm.compiler import NormCompiler
from typing import Optional


def compile_type_import(compiler: NormCompiler, atomic: bool, type_import: normParser.TypeImportContext,
                        comments: str) -> Optional[NormExecutable]:
    pass


