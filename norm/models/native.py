"""A collection of ORM sqlalchemy models for NativeLambda"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from sqlalchemy import exists

from norm.config import db
from norm.models.norm import Lambda, Variable, Status, retrieve_type

import logging
import traceback
logger = logging.getLogger(__name__)


class RegisterNatives(object):
    types = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, cls):
        self.types.append((cls, self.args, self.kwargs))
        return cls

    @classmethod
    def register(cls):
        for clz, args, kwargs in cls.types:
            instance = clz(*args, **kwargs)
            in_store = db.session.query(exists().where(clz.name == instance.name)).scalar()
            if not in_store:
                logger.info('Registering class {}'.format(instance.name))
                db.session.add(instance)
        try:
            db.session.commit()
        except:
            logger.error('Type registration failed')
            logger.debug(traceback.print_exc())

    @classmethod
    def retrieve(cls, clz, *args, **kwargs):
        instance = clz(*args, **kwargs)
        stored_inst = db.session.query(clz).filter(clz.name == instance.name).scalar()
        if stored_inst is None:
            stored_inst = instance
            db.session.add(instance)
        return stored_inst


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
        self.shape = []

    def empty_data(self):
        return None


@RegisterNatives()
class TypeLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_type'
    }

    def __init__(self):
        super().__init__(name='Type',
                         description='A logical function',
                         variables=[])


@RegisterNatives()
class AnyLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_any'
    }

    def __init__(self):
        super().__init__(name='Any',
                         description='Any type',
                         variables=[])


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


@RegisterNatives()
class BooleanLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_boolean'
    }

    def __init__(self):
        super().__init__(name='Boolean',
                         description='Boolean, true/false',
                         variables=[],
                         dtype='bool')


@RegisterNatives()
class FloatLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_float'
    }

    def __init__(self):
        super().__init__(name='Float',
                         description='Integer, -inf..+inf',
                         variables=[],
                         dtype='float')


@RegisterNatives()
class IntegerLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_integer'
    }

    def __init__(self):
        super().__init__(name='Integer',
                         description='Integer, -inf..+inf',
                         variables=[],
                         dtype='int')


@RegisterNatives()
class StringLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_string'
    }

    def __init__(self):
        super().__init__(name='String',
                         description='String, "blahbalh"',
                         variables=[])


@RegisterNatives()
class PatternLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_pattern'
    }

    def __init__(self):
        super().__init__(name='Pattern',
                         description='Pattern, r"^test[0-9]+"',
                         variables=[])


@RegisterNatives()
class UUIDLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_uuid'
    }

    def __init__(self):
        super().__init__(name='UUID',
                         description='UUID, $"sfsfsfsf"',
                         variables=[])


@RegisterNatives()
class URLLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_url'
    }

    def __init__(self):
        super().__init__(name='URL',
                         description='URL, l"http://example.com"',
                         variables=[])


@RegisterNatives()
class DatetimeLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_datetime'
    }

    def __init__(self):
        super().__init__(name='Datetime',
                         description='Datetime, t"2018-09-01"',
                         variables=[],
                         dtype='datetime64[ns]')


@RegisterNatives(dtype='float32', shape=[300])
class TensorLambda(NativeLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_native_tensor'
    }

    def __init__(self, dtype, shape):
        super().__init__(name='Tensor[{}]{}'.format(dtype, str(tuple(shape))),
                         description='Tensor, [2.2, 3.2]',
                         variables=[],
                         dtype=dtype)
        assert(isinstance(shape, list) or isinstance(shape, tuple))
        assert(all([isinstance(element, int) for element in shape]))
        self.shape = list(shape)
        self.ttype = dtype


def get_type_by_dtype(dtype):
    """
    Convert the numpy dtype to native lambda
    :param dtype: the numpy dtype
    :type dtype: numpy.dtype
    :return: the Lambda
    :rtype: Lambda
    """
    if dtype.name.find('int') > -1:
        return retrieve_type('norm.native', 'Integer')
    elif dtype.name.find('float') > -1:
        return retrieve_type('norm.native', 'Float')
    else:
        return retrieve_type('norm.native', 'Any')
