import logging

import pandas as pd

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON, Table
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

from norm.models import Model
from norm.utils import uuid_int32, random_name
from norm.config import USE_DASK, DataFrame
from norm.grammar import OUTPUT_VAR_STUB, TEMP_VAR_STUB

from typing import Dict, Any, List, Optional, TYPE_CHECKING, Union, TypeVar

if TYPE_CHECKING:
    from norm.models.norm import Lambda

logger = logging.getLogger(__name__)

V = TypeVar('V', int, float, str, bool, List, Dict)


class Variable(Model):
    __tablename__ = 'variables'

    category = Column(String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'variable',
        'polymorphic_on': category,
        'with_polymorphic': '*'
    }

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

    id = Column(Integer, primary_key=True, default=uuid_int32)
    name = Column(String(256), default='')
    asc = Column(Boolean)
    position = Column(Integer)
    stats = Column(JSON)
    scope_id = Column(Integer, ForeignKey('lambdas.id'))
    type_id = Column(Integer, ForeignKey('lambdas.id'))
    type_ = relationship('Lambda', foreign_keys=[type_id])

    def __init__(self, type_: "Lambda", name: str = None, default: V = None, asc: bool = None):
        """
        Construct the variable
        :param type_: the type of the variable
        :param name: the name of the variable
        :param default: the default value of the variable
        :param asc: order the objects according to the ascending order, default to None, i.e., no ordering
        """
        from norm.models.norm import Lambda
        self.id: int = uuid_int32()
        self.type_: Lambda = type_
        self.name: str = name or TEMP_VAR_STUB + random_name()
        self.stats: Dict = {}
        if default is not None:
            self.stats[self.KEY_DEFAULT] = default
        self.asc: bool = asc
        self._data: DataFrame = self.type_.empty_data if self.type_ else None

    def __repr__(self):
        return '{}: {}'.format(self.name, self.type_)

    def __str__(self):
        return self.__repr__()

    @property
    def dtype(self) -> str:
        return self.type_.dtype

    @property
    def default(self) -> V:
        return self.stats.get(self.KEY_DEFAULT, self.type_.default)

    @default.setter
    def default(self, v: V):
        self.stats[self.KEY_DEFAULT] = v

    @property
    def state(self) -> Optional[V]:
        return self.stats.get(self.KEY_STATE, None)

    @state.setter
    def state(self, value: V):
        assert(value is not None)
        self.stats[self.KEY_STATE] = value

    @property
    def max(self) -> V:
        return self.stats.get(self.KEY_MAX)

    @max.setter
    def max(self, v: V):
        self.stats[self.KEY_MAX] = v

    @property
    def min(self) -> V:
        return self.stats.get(self.KEY_MIN)

    @min.setter
    def min(self, v: V):
        self.stats[self.KEY_MIN] = v

    @property
    def mean(self) -> V:
        return self.stats.get(self.KEY_MEAN)

    @mean.setter
    def mean(self, v: V):
        self.stats[self.KEY_MEAN] = v

    @property
    def median(self) -> V:
        return self.stats.get(self.KEY_MEDIAN)

    @median.setter
    def median(self, v: V):
        self.stats[self.KEY_MEDIAN] = v

    @property
    def num_unique(self) -> int:
        return self.stats.get(self.KEY_NUM_UNIQUE)

    @num_unique.setter
    def num_unique(self, v: int):
        self.stats[self.KEY_NUM_UNIQUE] = v

    @property
    def num_na(self) -> int:
        return self.stats.get(self.KEY_NUM_NA)

    @num_na.setter
    def num_na(self, v: int):
        self.stats[self.KEY_NUM_NA] = v

    @property
    def count(self) -> int:
        return self.stats.get(self.KEY_COUNT, len(self._data))

    @count.setter
    def count(self, v: int):
        self.stats[self.KEY_COUNT] = v

    @property
    def scalar(self) -> Optional[V]:
        """
        Return the single object
        """
        if len(self._data) > 0:
            return self._data.iloc[0].to_dict()
        else:
            return None

    @scalar.setter
    def scalar(self, value: V):
        self._data.iloc[0, self._data.columns[0]] = value

    @property
    def data(self) -> DataFrame:
        """
        All data including positives, negatives and unknowns
        """
        return self._data

    @data.setter
    def data(self, value: Union[DataFrame, Dict]):
        if isinstance(value, dict):
            import pandas as pd
            data = pd.DataFrame(data=value)
            if USE_DASK:
                import dask.dataframe as dd
                data = dd.from_pandas(data, npartitions=1)
        elif isinstance(value, DataFrame):
            data = value
        else:
            msg = f'can not convert {type(value)} to DataFrame'
            logger.error(msg)
            raise TypeError(msg)
        self._data = data

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

    def __init__(self, type_: 'Lambda', name: str, default: V = None, asc: bool = None,
                 as_primary: bool = True, as_oid: bool = False, as_time: bool = False):
        """
        :param type_: the type of the variable
        :param name: the name of the variable
        :param default: the default value of the variable
        :param asc: order the objects according to the ascending order, default to None, i.e., no ordering
        :param as_primary: whether the variable is a primary variable, i.e., used to generate oid
        :param as_oid: whether the variable is treated as oid, i.e., _oid value is generated from this variable
        :param as_time: whether the variable is treated as time, i.e., _timestamp is a copy of this variable
        """
        super().__init__(type_, name, default, asc)
        self.as_primary = as_primary
        self.as_oid = as_oid
        self.as_time = as_time


class Output(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_output'
    }

    group = Column(Integer, default=0)

    def __init__(self, type_: 'Lambda', name: str = None, default: V = None, asc: bool = None, group: int = 0):
        """
        :param type_: the type of the variable
        :param name: the name of the variable
        :param default: the default value of the variable
        :param asc: order the objects according to the ascending order, default to None, i.e., no ordering
        :param group: the group number of outputs for multiple outputs, e.g. ()->(a:String, b:Integer)->String
        :type group: int
        """
        super().__init__(type_, name or OUTPUT_VAR_STUB + random_name(), default, asc)
        self.group = group


class Internal(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_internal'
    }

    stateful = Column(Boolean, default=False)

    def __init__(self, type_: 'Lambda', name: str, default: V = None, asc: bool = None, stateful: bool = False):
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

    def __init__(self, type_: 'Lambda', name: str):
        """
        External variable is a reference to a type object which is used to define the current type
        :param type_: the type of the variable
        :param name: the name of the variable
        """
        super().__init__(type_, name)


class Parameter(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_parameter'
    }

    KEY_INIT = 'initial'

    def __init__(self, type_: 'Lambda', name: str, initial: V, asc: bool = None):
        """
        Parameter variable that is the same value for all records
        :param type_: the type of the variable
        :param name: the name of the variable
        :param initial: the initial value of the variable, default to the type's default value
        :param asc: order the objects according to the ascending order, default to None, i.e., no ordering
        """
        super().__init__(type_, name, type_.default, asc)
        if initial is None:
            initial = type_.default
        self.stats[self.KEY_INIT] = initial


class Parent(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_parent'
    }

    PARENT_STUB = 'parent'

    def __int__(self, type_: 'Lambda'):
        """
        Parent variable is a reference to a type object which the current type is inherited from
        :param type_: the parent type object
        """
        super().__init__(type_, self.PARENT_STUB + random_name())


class Past(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_past'
    }

    def __init__(self, type_: 'Lambda'):
        """
        Past variable refers to itself with a previous version
        :param type_: the type with a past version
        """
        super(Past, self).__init__(type_, f'@{type_.signature}')


class Intern(Variable):
    __mapper_args__ = {
        'polymorphic_identity': 'variable_intern'
    }

    INTERN_STUB = 'intern'

    def __init__(self, type_: 'Lambda'):
        """
        Intern variable is reference to a type
        :param type_: the intern type
        """
        super().__init__(type_, self.INTERN_STUB + random_name())


class Const(Variable):

    __mapper_args__ = {
        'polymorphic_identity': 'variable_const'
    }

    def __init__(self, type_: 'Lambda', name: str, value: V):
        """
        A constant variable refers to a constant
        :param type_: the type of the constant
        :param name: the name of the variable
        :param value: the value of the variable
        """
        super(Const, self).__init__(type_, name)
        self._data: V = value

    @property
    def count(self) -> int:
        return 1

    @property
    def scalar(self) -> Optional[V]:
        return self._data

    @property
    def data(self) -> DataFrame:
        return DataFrame(data={self.name: [self._data]})

    @property
    def positives(self) -> DataFrame:
        return self.data

    @property
    def negatives(self) -> DataFrame:
        return DataFrame(data={self.name: []})

    @property
    def unknowns(self) -> DataFrame:
        return DataFrame(data={self.name: []})
