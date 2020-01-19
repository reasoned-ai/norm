import logging
from typing import List
from antlr4 import InputStream, CommonTokenStream
from sqlalchemy import desc
from sqlalchemy.orm.session import Session

from norm.models.norm import Module
from norm.compiler.exception import NormErrorListener, ParseError
from norm.compiler.planner import NormPlanner
from norm.executable import NormExecutable
from norm.grammar.normLexer import normLexer
from norm.grammar.normParser import normParser

logger = logging.getLogger(__name__)


class NormCompiler(object):

    def __init__(self, module):
        """
        :param module: the module compiler lives in
        :type module: Module
        """
        self.context: dict = {}
        self.python_context: dict = {}
        # noinspection PyTypeChecker
        self.session: Session = None
        self.current_module = module

    def set_python_context(self, v):
        self.python_context = v or {}
        return self

    def set_session(self, v):
        assert(v is not None)
        assert(isinstance(v, Session))
        self.session = v
        return self

    def compile(self, script):
        """
        Compile the script within the module
        :param script: the script of the module, can be incremental delta
        :type script: str
        :return: the norm executables
        :rtype: List[NormExecutable]
        """
        script = script
        try:
            lexer = normLexer(InputStream(script))
            stream = CommonTokenStream(lexer)
            parser = normParser(stream)
            parser.addErrorListener(NormErrorListener())
            module = parser.module()
        except ParseError as e:
            logger.error(f'Can not parse {script}')
            logger.error(e)
            raise e

        from norm.compiler.statement import Statement
        statements = []
        for ch in module.children:
            if isinstance(ch, normParser.Full_statementContext) and ch.statement():
                statements.extend(Statement(self).compile(ch.comments(), ch.statement()))
        return statements


class NormCompilable(object):
    def __init__(self, compiler):
        from norm.compiler import NormCompiler
        from norm.models.norm import Lambda
        self.compiler: NormCompiler = compiler
        self.lam: Lambda or None = None

    def get_module(self, full_name, version=None):
        """
        Get module by full name and version
        :type full_name: str
        :type version: str or None
        :rtype: norm.models.norm.Module or None
        """
        from norm.models.norm import Module
        q = self.compiler.session.query(Module)
        if version:
            return q.filter(Module.full_name == full_name, Module.version == version).scalar()
        else:
            return q.filter(Module.full_name == full_name).order_by(desc(Module.created_on)).first()

    def get_lambda(self, name, module=None, version=None):
        """
        Get lambda by name, module and version
        :type name: str
        :type module: norm.models.norm.Module or None
        :type version: str or None
        :rtype: norm.models.norm.Lambda or None
        """
        from norm.models.norm import Lambda
        q = self.compiler.session.query(Lambda)
        if not module:
            module = self.compiler.current_module
        if version:
            return q.filter(Lambda.module_id == module.id, Lambda.name == name, Lambda.version == version).scalar()
        else:
            return q.filter(Lambda.module_id == module.id, Lambda.name == name)\
                .order_by(desc(Lambda.created_on)).first()

    def compile(self, *args, **kwargs):
        """
        :rtype: List[NormExecutable]
        """
        raise NotImplementedError


class Variable(object):

    def __init__(self, name, pivot=False):
        """
        Variable placeholder. Pivoting variable is a formatted string
        :type name: str
        """
        self.name = name
        self.pivot = pivot


