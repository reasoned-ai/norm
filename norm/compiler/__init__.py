import logging
import traceback
from enum import Enum
from functools import lru_cache
from typing import List, Optional, Dict, Union

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from sqlalchemy.orm import Session
from sqlalchemy.orm.scoping import scoped_session

from norm.config import MAX_MODULE_CACHE_SIZE, DataFrame, EMPTY_DATA
from norm.executable import NormExecutable, Statements
from norm.parser.normLexer import normLexer
from norm.parser.normParser import normParser
from norm.models import norma
from norm.models.norm import Module, Lambda, Script
from norm.models.storage import Storage

logger = logging.getLogger(__name__)


class ParseError(ValueError):
    pass


class NormErrorListener(ErrorListener):
    def __init__(self):
        super(NormErrorListener, self).__init__()

    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
        err_msg = "line " + str(line) + ":" + str(column) + " " + msg
        raise ParseError(err_msg)


class CompileError(ValueError):
    pass


def error_on(cond: object = None, msg: str = ''):
    """
    Raise error if condition satisfied
    :param cond: the logical condition
    :param msg: the message to log
    :raise: CompileError
    """
    if cond:
        raise CompileError(msg)


def info_on(cond: object = None, msg: str = ''):
    """
    Log info if condition satisfied
    :param cond: the logical condition
    :param msg: the message to log
    """
    if cond:
        logger.info(msg)


def warn_on(cond: object = None, msg: str = ''):
    """
    Log warning if condition satisfied
    :param cond: the logical condition
    :param msg: the message to log
    """
    if cond:
        logger.warning(msg)


def same(array: List, another: List = None) -> bool:
    """
    Whether every element is the same or not if one array is provided.
    If two arrays are provided, compare each element.
    :param array: the array of element
    :param another: the other array of element to compare with
    """
    if another is None:
        if not isinstance(array, list) or len(array) <= 1:
            return True
        e = array[0]
        return all(a == e for a in array)
    else:
        if not isinstance(another, list) or not isinstance(array, list) or len(array) != len(another):
            return False
        return all(a1 == a2 for a1, a2 in zip(array, another))


class CodeType(Enum):
    NORM = ''
    PYTHON = 'python'
    SQL = 'sql'


class NormCompiler(object):

    def __init__(self, module_name: str, storage_name: str = 'unix_user_default'):
        """
        :param module_name: the module name compiler lives in
        """
        self.current_scope: Optional[Lambda] = None
        self.context: dict = {}
        self.data: DataFrame = EMPTY_DATA
        self.python_context: dict = {}
        self.session: Optional[Union[Session, scoped_session]] = None
        self.current_module_name: str = module_name
        self.current_storage_name: str = storage_name
        self.storage: Optional[Storage] = None
        self.current_module: Optional[Module] = None
        self.native_module: Optional[Module] = None
        self.core_module: Optional[Module] = None

    def set_python_context(self, v: Dict) -> "NormCompiler":
        self.python_context = v or {}
        return self

    def set_session(self, v: Union[Session, scoped_session]) -> "NormCompiler":
        assert(v is not None)
        assert(isinstance(v, (Session, scoped_session)))
        self.session = v
        self.current_scope = None

        if self.storage:
            self.storage = self.session.merge(self.storage)
        else:
            self.storage = norma._get_storage(self.current_storage_name)
            if self.storage is None:
                raise CompileError(f'Storage {self.current_storage_name} is not defined')

        if self.current_module:
            self.current_module = self.session.merge(self.current_module)
        else:
            self.current_module = norma._get_module(self.current_module_name)
            if self.current_module is None:
                self.current_module = norma.create_module(self.current_module_name, '', self.storage)
                assert(self.current_module is not None)

        if self.native_module:
            self.native_module = self.session.merge(self.native_module)
        else:
            self.native_module = norma['native']

        if self.core_module:
            self.core_module = self.session.merge(self.core_module)
        else:
            self.core_module = norma['core']

        return self

    def create_lambda(self, name: str, atomic: bool, code_type: CodeType) -> Optional["Lambda"]:
        if code_type == CodeType.NORM:
            return norma.create_lambda(name=name, module=self.current_module, atomic=atomic)
        elif code_type == CodeType.PYTHON:
            return norma.create_python_lambda(name=name, module=self.current_module, atomic=atomic)
        else:
            raise ParseError(f'{code_type} is not implemented yet')

    def get_lambda(self, name: str, version: str, module_name: str = None) -> Optional["Lambda"]:
        if module_name is not None:
            module_names = [module_name]
        else:
            module_names = [self.current_module.name, 'native', 'core']
        return norma.fetch_lambda(module_names, name, version)

    def compile(self, script):
        """
        Compile the script within the module
        :param script: the script of the module, can be incremental delta
        :type script: str
        :return: the norm executables
        :rtype: NormExecutable
        """
        if script is None or script.strip() == '':
            return None

        self.current_module.scripts.append(Script(content=script))
        try:
            lexer = normLexer(InputStream(script))
            stream = CommonTokenStream(lexer)
            parser = normParser(stream)
            parser.addErrorListener(NormErrorListener())
            parsed_script = parser.script()
        except ParseError as e:
            logger.error(f'Can not parse {script}')
            logger.error(e)
            logger.debug(traceback.print_exc())
            raise e

        from norm.compiler.statement import compile_statement
        statements = []
        ch: normParser.Full_statementContext
        for ch in parsed_script.getTypedRuleContexts(normParser.Full_statementContext):
            if ch.statement():
                statements.append(compile_statement(self, ch.comments(), ch.statement()))
        return Statements(self, dependents=statements)


@lru_cache(MAX_MODULE_CACHE_SIZE)
def build_compiler(module_name: str, storage_name: str = 'unix_user_default') -> NormCompiler:
    """
    :param module_name: the module name of the compiler
    :param storage_name: the name of the storage
    :return: the compiler
    """
    return NormCompiler(module_name, storage_name)

