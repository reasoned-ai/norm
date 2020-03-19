import logging

import pandas as pd

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from norm.models import Model
from norm.utils import uuid_int, random_name

logger = logging.getLogger(__name__)


class Variable(Model):
    __tablename__ = 'variables'

    category = Column(String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'variable',
        'polymorphic_on': category,
        'with_polymorphic': '*'
    }

    VAR_ANONYMOUS_STUB = 'var'

    # statistics
    KEY_DEFAULT = 'default'
    KEY_STATE = 'current'
    KEY_MAX = 'max'
    KEY_MIN = 'min'
    KEY_NUM_UNIQUE = 'num_unique'
    KEY_MEAN = 'mean'
    KEY_MEDIAN = 'median'
    KEY_NUM_NA = 'num_na'
    KEY_COUNT = 'count'

    id = Column(Integer, primary_key=True, default=uuid_int)
    name = Column(String(256), default='')
    asc = Column(Boolean)
    position = Column(Integer)
    stats = Column(JSON)
    scope_id = Column(Integer, ForeignKey('lambdas.id'))
    scope = relationship('Lambda', foreign_keys=[scope_id])
    type_id = Column(Integer, ForeignKey('lambdas.id'))
    type_ = relationship('Lambda', foreign_keys=[type_id])

    def __init__(self, type_, name='', default=None, asc=None):
        """
        Construct the variable
        :param type_: the type of the variable
        :type type_: norm.models.norm.Lambda
        :param name: the name of the variable
        :type name: str
        :param default: the default value
        :type default: object
        :param asc: order the objects according to the ascending order, default to None, i.e., no ordering
        :type asc: bool
        """
        self.id = uuid_int()
        self.type_ = type_
        self.name = name or self.VAR_ANONYMOUS_STUB + random_name()
        self.stats = {}
        self.default = default
        self.asc = asc
        self._data: pd.DataFrame = None

    def __repr__(self):
        return '{}: {}'.format(self.name, self.type_)

    def __str__(self):
        return self.__repr__()

    @property
    def dtype(self):
        raise NotImplementedError

    @property
    def default(self):
        return self.stats.get(self.KEY_DEFAULT, self.type_.default)

    @default.setter
    def default(self, v):
        self.stats[self.KEY_DEFAULT] = v

    @property
    def value(self):
        return self.stats.get(self.KEY_STATE, self.default)

    @value.setter
    def value(self, v):
        self.stats[self.KEY_STATE] = v

    @property
    def max(self):
        return self.stats.get(self.KEY_MAX, None)

    @max.setter
    def max(self, v):
        self.stats[self.KEY_MAX] = v

    @property
    def min(self):
        return self.stats.get(self.KEY_MIN, None)

    @min.setter
    def min(self, v):
        self.stats[self.KEY_MIN] = v

    @property
    def mean(self):
        return self.stats.get(self.KEY_MEAN, None)

    @mean.setter
    def mean(self, v):
        self.stats[self.KEY_MEAN] = v

    @property
    def median(self):
        return self.stats.get(self.KEY_MEDIAN, None)

    @median.setter
    def median(self, v):
        self.stats[self.KEY_MEDIAN] = v

    @property
    def num_unique(self):
        return self.stats.get(self.KEY_NUM_UNIQUE, None)

    @num_unique.setter
    def num_unique(self, v):
        self.stats[self.KEY_NUM_UNIQUE] = v

    @property
    def num_na(self):
        return self.stats.get(self.KEY_NUM_NA, None)

    @num_na.setter
    def num_na(self, v):
        self.stats[self.KEY_NUM_NA] = v

    @property
    def count(self):
        return self.stats.get(self.KEY_COUNT, None)

    @count.setter
    def count(self, v):
        self.stats[self.KEY_COUNT] = v

    @property
    def scalar(self):
        """
        Return the single value
        :rtype: Any
        """
        return self._data.iloc[0, self._data.columns[0]]

    @property
    def data(self):
        """
        All data including positives, negatives and unknowns
        :rtype: pd.DataFrame
        """
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def positives(self):
        """
        Positive results
        :rtype: pd.DataFrame
        """
        raise NotImplementedError

    @property
    def negatives(self):
        """
        Negative results
        :rtype: pd.DataFrame
        """
        raise NotImplementedError

    @property
    def unknowns(self):
        """
        Unknown results
        :rtype: pd.DataFrame
        """
        raise NotImplementedError


class Input(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_input'
    }

    as_primary = Column(Boolean, default=False)
    as_oid = Column(Boolean, default=False)
    as_time = Column(Boolean, default=False)

    def __init__(self, type_, name, default=None, asc=None,
                 as_primary=True, as_oid=False, as_time=False):
        """
        :type type_: norm.models.norm.Lambda
        :type name: str
        :type default: object
        :type asc: bool
        :param as_primary: whether the variable is a primary variable, i.e., used to generate oid
        :type as_primary: bool
        :param as_oid: whether the variable is treated as oid, i.e., _oid value is generated from this variable
        :type as_oid: bool
        :param as_time: whether the variable is treated as time, i.e., _timestamp is a copy of this variable
        :type as_time: bool
        """
        super().__init__(type_, name, default, asc)
        self.as_primary = as_primary
        self.as_oid = as_oid
        self.as_time = as_time


class Output(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_output'
    }

    as_primary = Column(Boolean, default=False)
    group = Column(Integer, default=0)

    def __init__(self, type_, name='', default=None, asc=None, group=0, as_primary=True):
        """
        :type type_: norm.models.norm.Lambda
        :type name: str
        :type default: object
        :type asc: bool
        :param group: the group number of outputs for multiple outputs, e.g. ()->(a:String, b:Integer)->String
        :type group: int
        :param as_primary: whether the variable is a primary variable, i.e., used to generate oid
        :type as_primary: bool
        """
        super().__init__(type_, name, default, asc)
        self.as_primary = as_primary
        self.group = group


class Internal(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_internal'
    }

    stateful = Column(Boolean, default=False)

    def __init__(self, type_, name, default=None, asc=None, stateful=False):
        """
        :type type_: norm.models.norm.Lambda
        :type name: str
        :type default: object
        :type asc: bool
        :param stateful: whether the variable is stateful or not. Stateful variable keeps the current value
        :type stateful: bool
        """
        super().__init__(type_, name, default, asc)
        self.stateful = stateful


class External(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_external'
    }

    def __init__(self, type_, name):
        """
        External variable is a reference to a type object which is used to define the current type
        :type type_: norm.models.norm.Lambda
        :type name: str
        """
        super().__init__(type_, name)


class Parameter(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_parameter'
    }

    def __init__(self, type_, name, default, asc=None):
        """
        Parameter variable that is the same value for all records
        :type type_: norm.models.norm.Lambda
        :type name: str
        :type default: object
        :type asc: bool
        """
        super().__init__(type_, name, default or type_.default, asc)


class Parent(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_parent'
    }

    PARENT_STUB = 'parent'

    def __int__(self, type_):
        """
        Parent variable is a reference to a type object which the current type is inherited from
        :type type_: norm.models.norm.Lambda
        """
        super().__init__(type_, self.PARENT_STUB + random_name())


class Intern(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_intern'
    }

    INTERN_STUB = 'intern'

    def __init__(self, type_):
        """
        Intern variable is reference to a type
        :type type_: norm.models.norm.Lambda
        """
        super().__init__(type_, self.INTERN_STUB + random_name())
