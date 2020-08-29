"""A collection of ORM sqlalchemy models for NativeLambda"""
from norm.models import norma, Register
from norm.models.norm import Lambda, Module
from norm.models.variable import Input, Output

from datetime import datetime
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from norm.models.variable import Variable
import numpy as np

import logging
logger = logging.getLogger(__name__)

__version__ = '1'


@Register()
class NativeModule(Module):
    __mapper_args__ = {
        'polymorphic_identity': 'module_native'
    }

    def __init__(self):
        super().__init__('native', description='Norm native namespace')


class NativeLambda(Lambda):

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native'
    }

    def __init__(self, name: str, description: str, bindings: List["Variable"] = None, dtype: str = 'object',
                 version: str = None):
        super().__init__(module=norma['native'],
                         name=name,
                         description=description,
                         version=version or __version__,
                         bindings=bindings)
        self.atomic = True
        self.dtype = dtype

    @property
    def empty_data(self):
        return None


@Register()
class TypeLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'native_type'
    }

    def __init__(self):
        super().__init__(name='Type', description='The generic type type')

    @property
    def default(self):
        return None


@Register()
class AnyLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'native_any'
    }

    def __init__(self):
        super().__init__(name='Any', description='The generic type')

    @property
    def default(self):
        return None


@Register()
class BooleanLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'native_boolean'
    }

    def __init__(self):
        super().__init__(name='Boolean',
                         description='Boolean, true/false',
                         dtype='bool')

    @property
    def default(self):
        return False


@Register()
class FloatLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'native_float'
    }

    def __init__(self):
        super().__init__(name='Float',
                         description='float, -inf..+inf',
                         dtype='float64')

    @property
    def default(self):
        return 0.0


@Register()
class IntegerLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'native_integer'
    }

    def __init__(self):
        super().__init__(name='Integer',
                         description='Integer, -inf..+inf',
                         dtype='int64')

    @property
    def default(self):
        return 0


@Register()
class StringLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'native_string'
    }

    def __init__(self):
        super().__init__(name='String', description='String, "blahbalh" or r"\\sfsfs" or f"sfsfs{a}"')

    @property
    def default(self):
        return ''


@Register()
class UUIDLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'native_uuid'
    }

    def __init__(self):
        super().__init__(name='UUID', description='UUID, e.g., $12ffbaf')

    @property
    def default(self):
        return ''


@Register()
class DatetimeLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'native_datetime'
    }

    def __init__(self):
        super().__init__(name='Datetime',
                         description='Datetime, any dateutils.parser allowed formats. timezone defaults to UTC'
                                     't2018-09, t09/2018'
                                     't12-24, t24/12'
                                     't2019-07-11T02:03:12.2323-04:00',
                         dtype='datetime64[ns]')

    @property
    def default(self):
        return np.datetime64(datetime.utcnow())


class OperatorLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'native_operator'
    }

    LHS = 'lhs'
    RHS = 'rhs'
    OUT = 'out'

    @property
    def default(self):
        return None


@Register(name='not', description='negation of logic')
@Register(name='negate', description='negation of arithmetic')
class UnaryOperator(OperatorLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'operator_unary'
    }

    def __init__(self, name: str, description: str, type_: Lambda = None, version: str = None):
        super().__init__(name, description,
                         bindings=[Input(type_ or norma['native.Any'], self.RHS),
                                   Output(norma['native.Any'], self.OUT)],
                         version=version)


@Register(name='and', description='conjunction of logic')
@Register(name='or', description='disjunction of logic')
@Register(name='xor', description='mutual exclusion of logic')
@Register(name='imply', description='implication of logic')
@Register(name='except', description='exception of logic')
@Register(name='otherwise', description='otherwise of logic')
@Register(name='add', description='addition of arithmetic')
@Register(name='subtract', description='subtraction of arithmetic')
@Register(name='multiply', description='multiplication of arithmetic')
@Register(name='divide', description='division of arithmetic')
@Register(name='modulo', description='modulo of arithmetic')
@Register(name='power', description='power of arithmetic')
@Register(name='gt', description='greater than of arithmetic')
@Register(name='ge', description='greater than or equal to of arithmetic')
@Register(name='lt', description='less than of arithmetic')
@Register(name='le', description='less than or equal to of arithmetic')
@Register(name='eq', description='equal to of arithmetic')
@Register(name='neq', description='not equal to of arithmetic')
@Register(name='in', description='within or between of arithmetic')
@Register(name='nin', description='not within or between of arithmetic')
@Register(name='like', description='similar to of arithmetic')
@Register(name='unlike', description='not similar to of arithmetic')
@Register(name='access', description='access sub and variable')
class BinaryOperator(OperatorLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'operator_binary'
    }

    def __init__(self, name: str, description: str, type_: Lambda = None, version: str = None):
        super().__init__(name, description,
                         bindings=[Input(type_ or norma['native.Any'], self.LHS),
                                   Input(type_ or norma['native.Any'], self.RHS),
                                   Output(type_ or norma['native.Any'], self.OUT)],
                         version=version)


def get_type_by_dtype(dtype: np.dtype) -> Lambda:
    """
    Convert the numpy dtype to native lambda
    :param dtype: the numpy dtype
    :type dtype: numpy.dtype
    :return: the Lambda
    :rtype: Lambda
    """
    if dtype.name.find('int') > -1:
        return norma['native.Integer']
    elif dtype.name.find('float') > -1:
        return norma['native.Float']
    elif dtype.name.find('datetime') > -1:
        return norma['native.DateTime']
    elif dtype.name.find('string') > -1:
        return norma['native.String']
    elif dtype.name.find('bool') > -1:
        return norma['native.Boolean']
    else:
        return norma['native.Any']
