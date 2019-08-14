"""A collection of ORM sqlalchemy models for NativeLambda"""
from pandas import Series, to_timedelta

from norm.models import Register
from norm.models.norm import Lambda, Variable, Status

from datetime import datetime
import numpy as np

import logging
logger = logging.getLogger(__name__)


class NativeLambda(Lambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native'
    }
    NAMESPACE = 'norm.native'

    def __init__(self, name, description, variables, dtype='object'):
        super().__init__(namespace=self.NAMESPACE,
                         name=name,
                         description=description,
                         variables=variables,
                         dtype=dtype)
        self.status = Status.READY
        self.atomic = True

    def empty_data(self):
        return None


@Register()
class TypeLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_type'
    }

    def __init__(self):
        super().__init__(name='Type',
                         description='A logical type',
                         variables=[])


@Register()
class AnyLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_any'
    }

    def __init__(self):
        super().__init__(name='Any',
                         description='Any type',
                         variables=[])

    def convert(self, data):
        return data

    @property
    def default(self):
        return None


class ListLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_list'
    }
    INTERN = 'intern'

    def __init__(self, type_):
        """
        :param type_: the intern type of the list
        :type type_: Lambda
        """
        variable = Variable(self.INTERN, type_)
        super().__init__(name='List[{}]'.format(type_.signature),
                         description='A list of a certain type',
                         variables=[variable])

    @property
    def default(self):
        return []


@Register()
class BooleanLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_boolean'
    }

    def __init__(self):
        super().__init__(name='Boolean',
                         description='Boolean, true/false',
                         variables=[],
                         dtype='bool')

    @property
    def default(self):
        return False


@Register()
class FloatLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_float'
    }

    def __init__(self):
        super().__init__(name='Float',
                         description='Integer, -inf..+inf',
                         variables=[],
                         dtype='float64')

    @property
    def default(self):
        return 0.0


@Register()
class IntegerLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_integer'
    }

    def __init__(self):
        super().__init__(name='Integer',
                         description='Integer, -inf..+inf',
                         variables=[],
                         dtype='int64')

    @property
    def default(self):
        return 0


@Register()
class StringLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_string'
    }

    def __init__(self):
        super().__init__(name='String',
                         description='String, "blahbalh"',
                         variables=[])

    @property
    def default(self):
        return ''


@Register()
class PatternLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_pattern'
    }

    def __init__(self):
        super().__init__(name='Pattern',
                         description='Pattern, p"^test[0-9]+"',
                         variables=[])

    @property
    def default(self):
        return ''


@Register()
class UUIDLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_uuid'
    }

    def __init__(self):
        super().__init__(name='UUID',
                         description='UUID, $"sfsfsfsf"',
                         variables=[])

    @property
    def default(self):
        return ''


@Register()
class URLLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_url'
    }

    def __init__(self):
        super().__init__(name='URL',
                         description='URL, l"http://example.com"',
                         variables=[])

    @property
    def default(self):
        return 'http://'


@Register()
class DatetimeLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_datetime'
    }

    def __init__(self):
        super().__init__(name='Datetime',
                         description='Datetime, t"2018-09-01 00:00:00"',
                         variables=[],
                         dtype='datetime64[ns]')

    @property
    def default(self):
        return np.datetime64(datetime.utcnow())


@Register()
class TimeLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_time'
    }

    def __init__(self):
        super().__init__(name='Time',
                         description='Time, t"13:01:00"',
                         variables=[],
                         dtype='timedelta64[ns]')

    def convert(self, data):
        if not isinstance(data, Series) or self.dtype == data.dtype:
            return data

        return to_timedelta(data.fillna(self.default))

    @property
    def default(self):
        return np.timedelta64(0)


def get_type_by_dtype(dtype):
    """
    Convert the numpy dtype to native lambda
    :param dtype: the numpy dtype
    :type dtype: numpy.dtype
    :return: the Lambda
    :rtype: Lambda
    """
    from norm.models import lambdas
    if dtype.name.find('int') > -1:
        return lambdas.Integer
    elif dtype.name.find('float') > -1:
        return lambdas.Float
    else:
        return lambdas.Any
