"""A collection of ORM sqlalchemy models for CoreLambda"""
import ast
import logging
from textwrap import dedent, indent
from typing import List

from norm.models.mixins import lazy_property

from norm.executable import NormError
from sqlalchemy import Column, Text, String, orm

from norm.models import store, Registrable, Register
from norm.models.norm import Lambda, Module
from norm.models.variable import Variable

logger = logging.getLogger(__name__)

__version__ = '1'


@Register()
class CoreModule(Module):
    __mapper_args__ = {
        'polymorphic_identity': 'module_core'
    }

    def __init__(self):
        super().__init__('norm.core', description='Norm core namespace', version=__version__)


store_core = store.norm.core


class CoreLambda(Lambda, Registrable):
    """
    Core functions are at the computable level and predefined in the code base
    """
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core'
    }

    def __init__(self, name, description, bindings=None):
        """
        Norm core types
        :type name: str
        :type description: str
        :type bindings: List[Variable]
        """
        super().__init__(module=store_core.latest,
                         name=name,
                         description=description,
                         version=__version__,
                         bindings=bindings)
        self.atomic = True

    def exists(self):
        return [CoreLambda.name == self.name,
                CoreLambda.version == self.version]

    def empty_data(self):
        return None


@Register()
class PythonLambda(CoreLambda):

    code = Column(Text, default='')
    python_version = Column(String(8), default='3.7')
    python_packages = Column(Text, default='')

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core_python'
    }

    def __init__(self, name, description, code, bindings=None):
        """
        Python function, inputs are wrapped into one variable, outputs are one variable too.
        :param name: the name of the function
        :type name: str
        :param description: description
        :type description: str
        :param code: the code of the Python implementation
        :type code: str

        """
        super().__init__(name=name,
                         description=description,
                         bindings=bindings)
        self.code = dedent(code).strip(' \n')
        self.atomic = True

    def decorated(self):
        """
        Decorate code with a function definition
        """
        stmts = self.code.split('\n')
        if not stmts[-1].startswith('return'):
            stmts[-1] = 'return ' + stmts[-1]
            script = indent('\n'.join(stmts), prefix='  ')
        else:
            script = indent(self.code, prefix='  ')

        return "def func(" + ",".join(v.name for v in self.input_variables) + "):\n" + script + "\n"

    @lazy_property
    def func(self):
        try:
            d = {}
            exec(self.decorated(), d)
            return d.get('func')
        except Exception:
            msg = 'Can not load the python code: \n{}'.format(self.code)
            raise NormError(msg)
