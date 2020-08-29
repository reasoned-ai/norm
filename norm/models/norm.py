"""A collection of ORM sqlalchemy models for Lambda"""
import logging
from datetime import datetime
from textwrap import dedent, indent
from typing import Dict, List, Any, Union, Optional

from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy import String, Boolean, orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
import numpy as np
import pandas as pd

from norm.grammar import TEMP_VAR_STUB, OUTPUT_VAR_STUB
from norm.models import Model, Registrable, ModelError, norma
from norm.models.storage import Storage
from norm.models.variable import Variable, Output, Input, Parameter, Parent, Internal, External, Intern, Past
from norm.utils import uuid_int32, new_version, lazy_property, uuid_int, random_name
from norm.config import USE_DASK, DataFrame

logger = logging.getLogger(__name__)

metadata = Model.metadata


class Script(Model):
    """Script is a Norm script"""
    __tablename__ = 'scripts'

    id = Column(Integer, primary_key=True, default=uuid_int32)
    position = Column(Integer)
    content = Column(Text, nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"))
    created_on = Column(DateTime, default=datetime.utcnow)


class Module(Model, Registrable):
    """Module is a Norm namespace"""
    __tablename__ = 'modules'

    category = Column(String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'module',
        'polymorphic_on': category,
        'with_polymorphic': '*'
    }

    id = Column(Integer, primary_key=True, default=uuid_int32)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, default='')
    storage_id = Column(Integer, ForeignKey(Storage.id), nullable=False)
    storage = relationship(Storage)

    lambdas = relationship("Lambda", back_populates="module")
    scripts = relationship(Script, order_by=Script.position, collection_class=ordering_list('position'),
                           backref='module', foreign_keys=[Script.module_id])

    created_on = Column(DateTime, default=datetime.utcnow)
    changed_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, description=None, storage=None):
        super(Module, self).__init__()
        self.id: int = uuid_int32()
        self.name: str = name
        self.description: str = description or ""
        self.storage: Storage = storage or norma['storage.unix_user_default']
        self.lambdas: List["Lambda"] = []
        self.scripts: List[Script] = []

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        if self.id is not None:
            return self.id
        return hash(self.name)

    def __eq__(self, other: object):
        return self.__class__ is not other.__class__ and hash(self) == hash(other)

    def exists(self) -> List:
        return [Module.name == self.name]

    def copy(self, from_obj: "Registrable"):
        pass


class Lambda(Model, Registrable):
    """Lambda models a relation in Norm"""

    __tablename__ = 'lambdas'

    category = Column(String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'lambda',
        'polymorphic_on': category,
        'with_polymorphic': '*'
    }

    VAR_VALUE = '_value'
    VAR_VALUE_T = 'float'
    VAR_OID = '_oid'
    VAR_OID_T = 'int64'
    VAR_PROB = '_prob'
    VAR_PROB_T = 'float'
    VAR_TIME = '_time'
    VAR_TIME_T = 'datetime64[ns]'
    VAR_TOMBSTONE = '_tombstone'
    VAR_TOMBSTONE_T = 'bool'

    id = Column(Integer, primary_key=True, default=uuid_int32)
    name = Column(String(256), nullable=False)
    version = Column(String(32), default=new_version, nullable=False)
    description = Column(Text, default='')

    created_on = Column(DateTime, default=datetime.utcnow)
    changed_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    module_id = Column(Integer, ForeignKey(Module.id), nullable=False)
    module = relationship(Module, back_populates='lambdas')

    bindings = relationship(Variable, order_by=Variable.position, collection_class=ordering_list('position'),
                            backref='scope', foreign_keys=[Variable.scope_id])

    definition = Column(Text, default='')
    dtype = Column(String(8), default='object')
    trainable = Column(Boolean, default=False)
    atomic = Column(Boolean, default=False)

    # noinspection PyMissingConstructor
    def __init__(self, module: Module = None, name: str = '', description: str = '', version: str = '',
                 atomic: bool = False, bindings: List[Variable] = None):
        """
        :param module: the module that holds the type
        :param name: the name of the type
        :param description: the description of the type
        :param version: the version of the type
        :param atomic: whether it is the atomic type, i.e., constants and functions
        :param bindings: a ordered list of variables that refers to other types
        """
        self.module: Module = module
        self.id: int = uuid_int32()
        self.name: str = name
        self.description: str = description
        self.version: str = version or new_version()
        self.bindings: List[Variable] = bindings or []
        self.atomic: bool = atomic
        self.definition: str = ''
        self.trainable: bool = False
        if self.bindings:
            for v in self.bindings:
                v.scope = self
        self._data = self.empty_data

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.signature

    def __hash__(self) -> int:
        if self.id is not None:
            return self.id
        h = 0
        if self.module:
            h += hash(self.module_id) << 7
        h += hash(self.name) << 7
        if self.version:
            h += hash(self.version)
        return h

    def __eq__(self, other: object) -> bool:
        return self.__class__ is not other.__class__ and hash(self) == hash(other)

    def __contains__(self, item: Union[Variable, str]) -> bool:
        if isinstance(item, Variable):
            return item.name in self._schema_names

        if isinstance(item, str):
            return item in self._schema_names

        return False

    def func(self, data: DataFrame) -> DataFrame:
        """
        Evaluation function
        :param data: apply func on data
        :return: the computed objects if it is functional, otherwise computed probability for the objects
        """
        raise NotImplementedError

    @orm.reconstructor
    def init_on_load(self):
        self._data = self.empty_data
        if not self.atomic:
            self._load_data()
        if self.trainable:
            self._load_model()

    def exists(self):
        module_id = self.module_id if self.module is None else self.module.id
        return [Lambda.module_id == module_id,
                Lambda.name == self.name,
                Lambda.version == self.version]

    def copy(self, from_obj: "Registrable"):
        assert(isinstance(from_obj, Lambda))
        self._data = from_obj._data

    def get(self, item: str) -> Optional[Variable]:
        """
        The variable to get
        :param item: the attribute name
        :return: the variable
        """
        for b in self.bindings:
            if b.name == item:
                return b
        return None

    @lazy_property
    def _schema_names(self) -> List[str]:
        """
        :return: the input/output variable names
        """
        cols = [self.VAR_OID, self.VAR_TIME, self.VAR_VALUE, self.VAR_PROB] +\
               [v.name for v in self.inputs] +\
               [v.name for v in self.outputs]
        return cols

    @lazy_property
    def _schema_dtypes(self) -> Dict[str, str]:
        """
        :return: the dtypes for input/output variables
        """
        dtypes = dict((v.name, v.dtype) for v in self.inputs + self.outputs)
        dtypes[self.VAR_OID] = self.VAR_OID_T if self.oid_var is None else 'object'
        dtypes[self.VAR_TIME] = self.VAR_TIME_T
        dtypes[self.VAR_VALUE] = self.VAR_VALUE_T
        dtypes[self.VAR_PROB] = self.VAR_PROB_T
        return dtypes

    @lazy_property
    def empty_data(self) -> DataFrame:
        import pandas as pd
        d = pd.DataFrame(columns=self._schema_names).astype(self._schema_dtypes)
        if USE_DASK:
            import dask.dataframe as dd
            return dd.from_pandas(d, npartitions=1)
        return d

    def random_var(self):
        return Variable(self, TEMP_VAR_STUB + random_name())

    @lazy_property
    def parents(self) -> List[Variable]:
        """
        :return: Parent variables
        """
        return [v for v in self.bindings if isinstance(v, Parent)]

    @lazy_property
    def past(self) -> Optional[Variable]:
        """
        :return: Past variable, single timeline
        """
        for v in self.bindings:
            if isinstance(v, Past):
                return v
        return None

    @lazy_property
    def inputs(self) -> List[Input]:
        """
        :return: Input variables
        """
        # TODO scopes of parent inputs are different
        variables = []
        var_names = set()
        for p in self.parents:
            for v in p.type_.inputs:
                if v.name not in var_names:
                    variables.append(v)
                    var_names.add(v.name)
        for v in self.bindings:
            if isinstance(v, Input) and v.name not in var_names:
                variables.append(v)
                var_names.add(v.name)
        return variables

    @lazy_property
    def outputs(self) -> List[Output]:
        """
        :return: Output variables
        """
        # TODO scopes of parent outputs are different
        variables = []
        var_names = set()
        for p in self.parents:
            for v in p.type_.outputs:
                if v.name not in var_names:
                    variables.append(v)
                    var_names.add(v.name)
        for v in self.bindings:
            if isinstance(v, Output) and v.name not in var_names:
                variables.append(v)
                var_names.add(v.name)
        return variables

    @lazy_property
    def internals(self) -> List[Internal]:
        """
        :return: Internal variables
        """
        return [v for v in self.bindings if isinstance(v, Internal)]

    @lazy_property
    def externals(self) -> List[External]:
        """
        :return: External variables
        """
        return [v for v in self.bindings if isinstance(v, External)]

    @lazy_property
    def parameters(self) -> List[Parameter]:
        """
        :return: Parameter variables
        """
        # TODO scopes of parent parameters are different
        variables = []
        var_names = set()
        for p in self.parents:
            for v in p.type_.parameters:
                if v.name not in var_names:
                    variables.append(v)
                    var_names.add(v.name)
        for v in self.bindings:
            if isinstance(v, Parameter) and v.name not in var_names:
                variables.append(v)
                var_names.add(v.name)
        return variables

    @lazy_property
    def primaries(self) -> List[Union[Input, Output]]:
        """
        :return: Primary variables
        """
        return [v for v in self.bindings if isinstance(v, (Input, Output)) and v.as_primary]

    @lazy_property
    def default(self) -> Dict:
        """
        :return: The default value for the Lambda
        :rtype: Dict[str, Any]
        """
        rt = dict()
        for v in self.primaries:
            value = v.default
            if isinstance(value, dict):
                value = str(value[self.VAR_OID])
            rt[v.name] = value
        if self.oid_var:
            rt[self.VAR_OID] = rt[self.oid_var]
        else:
            rt[self.VAR_OID] = self.generate_oid(rt)
        return rt

    @lazy_property
    def is_functional(self) -> bool:
        """
        Whether the Lambda has any output variables
        """
        return any(self.outputs)

    @lazy_property
    def oid_var(self) -> Optional[Variable]:
        """
        :return: the oid variable
        """
        for v in self.inputs:
            if v.as_oid:
                return v
        return None

    @lazy_property
    def time_var(self) -> Optional[Variable]:
        """
        :return: the time variable
        """
        for v in self.inputs:
            if v.as_time:
                return v
        return None

    @property
    def signature(self) -> str:
        return f"{self.module}.{self.name}${self.version}"

    @classmethod
    def generate_oid(cls, value: Dict[str, Any]) -> int:
        key = ''
        for k, v in value.items():
            if isinstance(v, dict):
                key += str(v[cls.VAR_OID])
            else:
                key += str(v)
        return uuid_int(key)

    def fill_primary(self, df: DataFrame) -> DataFrame:
        """
        Fill empty primary variables with default values
        :param df: the dataframe to fill
        :return: the dataframe
        """
        cols = set(df.columns)
        for var in self.primaries:
            if var.name in cols:
                df[var.name] = df[var.name].fillna(var.default)
            else:
                df[var.name] = var.default
        return df

    def fill_oid(self, df: DataFrame) -> DataFrame:
        """
        Fill oid for data
        :param df: the dataframe to fill
        :return: the dataframe
        """
        if self.oid_var is not None:
            # if OID column is given
            assert(self.oid_var.name in set(df.columns))
            df[self.VAR_OID] = df[self.oid_var.name]
        else:
            # otherwise, primary columns are used to generate the oid and backfill it
            c = None
            for col in self.primaries:
                if c is None:
                    c = df[col].astype(str)
                else:
                    c = c.str.cat(df[col].astype(str))
            assert(c is not None)
            df[self.VAR_OID] = c.str.encode('utf-8').apply(uuid_int).astype('int64')
        return df

    def fill_time(self, df: DataFrame) -> DataFrame:
        if self.time_var is not None and self.time_var.name in df.columns:
            df[self.VAR_TIME] = df[self.time_var.name].astype('datetime64[ns]')
        else:
            if self.VAR_TIME in df.columns:
                df[self.VAR_TIME] = df[self.VAR_TIME].fillna(pd.to_datetime(datetime.utcnow()))
            else:
                df[self.VAR_TIME] = pd.to_datetime(datetime.utcnow())
        return df

    def save(self):
        """
        Save the current version
        """
        if not self.atomic:
            self._save_data()
        if self.trainable:
            self._save_model()

    @property
    def data(self) -> DataFrame:
        return self._data

    def _load_data(self):
        """
        Load data
        p: Past = self.past
        # TODO: load from storage
        curr: DataFrame = DataFrame()
        if USE_DASK:
            import dask.dataframe as dd
            self._data = dd.merge(p.type_.data, curr)
        else:
            self._data = pd.merge(p.type_.data, curr)
        """
        return

    def _save_data(self):
        # TODO: save to storage
        pass

    def _build_model(self):
        """
        Build an adaptable model
        TODO: to implement
        """
        pass

    def _load_model(self):
        """
        Load an adapted model
        TODO: to implement
        :return:
        """
        pass

    def _save_model(self):
        """
        Save an adapted model
        TODO: to implement
        :return:
        """
        pass


class UnionLambda(Lambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_union'
    }

    def __init__(self, interns: List[Lambda], module: Module):
        """
        :type interns: List[Lambda]
        :type module: Module
        """
        assert(interns is not None)
        assert(len(interns) > 0)
        name = '|'.join(t.signature for t in interns)
        super().__init__(module=module, name=name, bindings=[Intern(t) for t in interns])

    @property
    def default(self) -> Dict:
        """
        The first type's default
        :return: the default value for the union of types
        """
        return self.bindings[0].default

    @lazy_property
    def empty_data(self) -> DataFrame:
        raise NotImplementedError


class HigherOrderLambda(Lambda):
    level = Column(Integer, default=1)

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_higher_order'
    }

    def __init__(self, intern: Lambda, module: Module = None, level: int = 1):
        """
        :param intern: the super-type, e.g., [People] implies the value can be any sub-type of People
        :param module: the module this higher order lambda belongs to
        :param level: the level in the type hierarchy. [T] is level 1, while [[T]] is level 2, and etc.
        """
        assert(level > 0)
        assert(intern is not None)
        self.level = level
        name = ''.join(['['] * level + [intern.signature] + [']'] * level)
        super().__init__(module=module, name=name, bindings=[Intern(intern)])

    @property
    def default(self):
        return f'@{self.bindings[0].type_.signature}'

    @lazy_property
    def empty_data(self) -> DataFrame:
        raise NotImplementedError


class PythonLambda(Lambda):

    python_version = Column(String(8), default='3.7')
    python_packages = Column(Text, default='')

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_python'
    }

    def __init__(self, name: str, description: str, code: str = '', python_version: str = '3.7',
                 module: Module = None, version: str = None, bindings: List[Variable] = None):
        """
        Python function, inputs are wrapped into one variable, outputs are one variable too.
        :param name: the name of the lambda
        :param description: the description of the python function
        :param code: the code of the python function
        :param python_version: the version of the python interpreter
        :param module: the module this lambda belongs to
        :param version: the version of the lambda
        :param bindings: the parameters of the python function
        """
        super().__init__(name=name,
                         description=description,
                         module=module,
                         version=version,
                         atomic=True,
                         bindings=bindings)
        self.define(code)
        self.python_version = python_version

    def define(self, code: str):
        """
        Define the lambda by python code
        """
        self.definition = dedent(code).strip(' \n')

    @property
    def _decorated_code(self):
        """
        Decorate code with a function definition
        """
        stmts = self.definition.split('\n')
        if stmts[-1].startswith('return'):
            script = indent(self.definition, prefix='  ')
            return "def func(" + ",".join(v.name for v in self.inputs) + "):\n" + script + "\n"
        else:
            stmts[-1] = 'func = ' + stmts[-1]
            return '\n'.join(stmts)

    @lazy_property
    def func(self):
        try:
            d = {}
            exec(self._decorated_code, d)
            return d.get('func')
        except Exception:
            msg = 'Can not load the python code: \n{}'.format(self.definition)
            raise ModelError(msg)

    @property
    def default(self):
        raise NotImplementedError

    @lazy_property
    def empty_data(self) -> DataFrame:
        raise NotImplementedError


class SQLLambda(Lambda):

    sql_url = Column(String(128), default='')

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_sql'
    }

    def __init__(self, name: str, description: str, code: str = '', sql_url: str = '',
                 module: Module = None, version: str = None, bindings: List[Variable] = None):
        """
        SQL function, inputs are wrapped into one variable, outputs are one variable too.
        :param name: the name of the SQL query
        :param description: the description of the SQL query
        :param code: the SQL code
        :param sql_url: the SQLAlchemy engine url
        :param module: the module the lambda belongs to
        :param version: the version of the lambda
        :param bindings: the variables the SQL query results bind to
        """
        super().__init__(name=name,
                         description=description,
                         module=module,
                         version=version,
                         atomic=True,
                         bindings=bindings)
        self.definition = dedent(code).strip(' \n')
        self.sql_url = sql_url

    @lazy_property
    def func(self):
        # TODO: build a query function to SQL
        raise NotImplementedError

    @property
    def default(self):
        raise NotImplementedError

    @lazy_property
    def empty_data(self) -> DataFrame:
        raise NotImplementedError

