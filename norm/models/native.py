"""A collection of ORM sqlalchemy models for NativeLambda"""
import traceback

from norm.models import store
from norm.models.norm import Lambda, Variable

from datetime import datetime
import numpy as np

import logging
logger = logging.getLogger(__name__)


class NativeLambda(Lambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native'
    }

    def __init__(self, name, description, bindings=None, dtype='object'):
        super().__init__(module=store.norm.native.latest,
                         name=name,
                         description=description,
                         bindings=bindings)
        self.atomic = True
        self.dtype = dtype

    def empty_data(self):
        return None


class _register(object):
    types = []

    def __call__(self, cls):
        self.types.append(cls)
        return cls

    @classmethod
    def register(cls):
        from norm.config import session
        for clz in cls.types:
            instance = clz()
            in_store = session.query(NativeLambda).filter(NativeLambda.name == instance.name)
            if not in_store:
                logger.info('Registering class {}'.format(instance.name))
                session.add(instance)
        try:
            session.commit()
        except:
            logger.error('Type registration failed')
            logger.debug(traceback.print_exc())
            session.rollback()


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
        super().__init__(name='[{}]'.format(type_.signature),
                         description='Type of a type, either an type object that produces a list of objects, '
                                     'or just a list of objects',
                         bindings=[Variable(self.INTERN, type_)])

    @property
    def default(self):
        return []


@_register()
class TypeLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_type'
    }

    def __init__(self):
        super().__init__(name='Type', description='The generic higher order type')

    @property
    def default(self):
        return None


@_register()
class AnyLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_any'
    }

    def __init__(self):
        super().__init__(name='Any', description='The generic type')

    @property
    def default(self):
        return None


@_register()
class BooleanLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_boolean'
    }

    def __init__(self):
        super().__init__(name='Boolean',
                         description='Boolean, true/false',
                         dtype='bool')

    @property
    def default(self):
        return False


@_register()
class FloatLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_float'
    }

    def __init__(self):
        super().__init__(name='Float',
                         description='float, -inf..+inf',
                         dtype='float64')

    @property
    def default(self):
        return 0.0


@_register()
class IntegerLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_integer'
    }

    def __init__(self):
        super().__init__(name='Integer',
                         description='Integer, -inf..+inf',
                         dtype='int64')

    @property
    def default(self):
        return 0


@_register()
class StringLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_string'
    }

    def __init__(self):
        super().__init__(name='String', description='String, "blahbalh" or r"\\sfsfs" or f"sfsfs{a}"')

    @property
    def default(self):
        return ''


@_register()
class UUIDLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_uuid'
    }

    def __init__(self):
        super().__init__(name='UUID', description='UUID, e.g., $12ffbaf')

    @property
    def default(self):
        return ''


@_register()
class DatetimeLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_datetime'
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


def register_lambdas():
    _register.register()


def get_type_by_dtype(dtype):
    """
    Convert the numpy dtype to native lambda
    :param dtype: the numpy dtype
    :type dtype: numpy.dtype
    :return: the Lambda
    :rtype: Lambda
    """
    if dtype.name.find('int') > -1:
        return store.norm.native.Integer.latest
    elif dtype.name.find('float') > -1:
        return store.norm.native.Float.latest
    elif dtype.name.find('datetime') > -1:
        return store.norm.native.DateTime.latest
    else:
        return store.norm.native.Any.latest
