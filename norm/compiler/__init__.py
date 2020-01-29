import logging
import traceback
from enum import Enum
from functools import lru_cache
from typing import List

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from sqlalchemy import desc, func
from sqlalchemy.orm.session import Session

from norm.config import MAX_MODULE_CACHE_SIZE
from norm.executable import NormExecutable
from norm.grammar.normLexer import normLexer
from norm.grammar.normParser import normParser
from norm.models.norm import Module, Lambda, PythonLambda, SQLLambda

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


def error_on(cond=None, msg=''):
    """
    Raise error if condition satisfied
    :param cond: the logical condition
    :type cond: object
    :param msg: the message to log
    :type msg: str
    :raise: CompileError
    """
    if cond:
        raise CompileError(msg)


def info_on(cond=None, msg=''):
    """
    Log info if condition satisfied
    :param cond: the logical condition
    :type cond: object
    :param msg: the message to log
    :type msg: str
    """
    if cond:
        logger.info(msg)


def warn_on(cond=None, msg=''):
    """
    Log warning if condition satisfied
    :param cond: the logical condition
    :type cond: object
    :param msg: the message to log
    :type msg: str
    """
    if cond:
        logger.warning(msg)


def same(array, another=None):
    """
    Whether every element is the same or not if one array is provided.
    If two arrays are provided, compare each element.
    :param array: the array of element
    :type array: list
    :type another: list or None
    :rtype: bool
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

    def __init__(self, module_name):
        """
        :param module_name: the module name compiler lives in
        :type module_name: str
        """
        self.current_module: Module = self.get_module(module_name)
        self.native_module: Module = self.get_module('norm.native')
        self.core_module: Module = self.get_module('norm.core')

        self.current_scope: Lambda or None = None

        self.context: dict = {}
        self.python_context: dict = {}

        self.session: Session or None = None

    def set_python_context(self, v):
        self.python_context = v or {}
        return self

    def set_session(self, v):
        assert(v is not None)
        assert(isinstance(v, Session))
        self.session = v
        self.current_scope = None
        if self.current_module:
            self.session.merge(self.current_module)
        if self.native_module:
            self.session.merge(self.native_module)
        if self.core_module:
            self.session.merge(self.core_module)
        return self

    def get_module(self, name):
        """
        Get module by full name and version
        :type name: str
        :rtype: norm.models.norm.Module or None
        """
        if not name:
            return None

        module = self.context.get(name)
        if module:
            self.session.merge(module)
            return module

        from norm.models.norm import Module
        q = self.session.query(Module)
        module = q.filter(func.lower(Module.name) == func.lower(name)).scalar()

        if module is None:
            module = Module(name)
            self.session.add(module)

        self.context[name] = module
        return module

    def get_lambda(self, name, module=None, version=None, description='', atomic=False, code_type=CodeType.NORM,
                   bindings=None):
        """
        Get lambda by name, module and version
        :type name: str
        :type module: norm.models.norm.Module or None
        :type version: str or None
        :type description: str
        :type atomic: bool
        :type code_type: CodeType
        :type bindings: List[Variable]
        :rtype: Lambda or None
        """
        if not name:
            return None

        key = (name, module, version)
        lam = self.context.get(key)
        if lam:
            self.session.merge(lam)
            return lam

        q = self.session.query(Lambda)
        conds = [func.lower(Lambda.name) == func.lower(name)]
        if module:
            conds.append(Lambda.module_id == module.id)
        else:
            conds.append(Lambda.module_id.in_([self.current_module.id,
                                               self.core_module.id,
                                               self.native_module.id]))
        if version:
            conds.append(Lambda.version == version)
            lam = q.filter(conds).scalar()
        else:
            lam = q.filter(conds).order_by(desc(Lambda.created_on)).first()

        if lam is None:
            error_on(module is not None and module is not self.current_module,
                     f'{name}${version} does not exist in {module.full_name} yet')
            if code_type == CodeType.PYTHON:
                L = PythonLambda
            elif code_type == CodeType.SQL:
                L = SQLLambda
            else:
                L = Lambda
            lam = L(module=self.current_module,
                    name=name,
                    description=description,
                    version=version,
                    atomic=atomic,
                    bindings=bindings)
            self.session.add(lam)

        self.context[key] = lam
        return lam

    def compile(self, script):
        """
        Compile the script within the module
        :param script: the script of the module, can be incremental delta
        :type script: str
        :return: the norm executables
        :rtype: NormExecutable
        """
        self.current_module.set_script(script)
        try:
            lexer = normLexer(InputStream(script))
            stream = CommonTokenStream(lexer)
            parser = normParser(stream)
            parser.addErrorListener(NormErrorListener())
            module = parser.module()
        except ParseError as e:
            logger.error(f'Can not parse {script}')
            logger.error(e)
            logger.debug(traceback.print_exc())
            raise e

        from norm.compiler.statement import compile_statement
        statements = []
        ch: normParser.Full_statementContext
        for ch in module.getTypedRuleContexts(normParser.Full_statementContext):
            if ch.statement():
                statements.append(compile_statement(self, ch.comments(), ch.statement()))
        return NormExecutable(self, dependents=statements)


@lru_cache(MAX_MODULE_CACHE_SIZE)
def build_compiler(module_name):
    """
    :param module_name: the module name of the compiler
    :type module_name: str
    :return: the compiler
    :rtype: NormCompiler
    """
    return NormCompiler(module_name)

