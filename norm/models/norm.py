"""A collection of ORM sqlalchemy models for Lambda"""
import zlib

import norm.config as config
from norm.models.exception import InvalidDeclaration
from norm.models.mixins import lazy_property, AuditableMixin
from norm.models.license import License
from norm.models.security import User
from norm.models import Model
from norm.models.storage import Storage
from norm.utils import uuid_int, new_version, random_name

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime, Enum, desc, UniqueConstraint, \
    orm, LargeBinary, JSON
from sqlalchemy import Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.orderinglist import ordering_list

import os
import errno
import enum

from datetime import datetime
from pandas import DataFrame, to_timedelta, Series
import numpy as np

from typing import List, Dict

import logging
logger = logging.getLogger(__name__)

metadata = Model.metadata


class VariableSorting(enum.Enum):
    desc = 1
    asc = 2
    none = 3


class VariableCategory(enum.Enum):
    input = 1        # input free variable, stateless primary unless specified as optional
    output = 2       # output bound variable, stateless primary unless specified as optional
    internal = 3     # internal bound variable, stateless optional unless specified as primary
    dependent = 4    # dependent type variable, stateless optional
    parameter = 5    # parameter bound variable, stateful optional


class Variable(Model, AuditableMixin):
    """Variable placeholder"""

    __tablename__ = 'variables'

    VAR_ANONYMOUS_STUB = 'var'

    KEY_DEFAULT = 'default'
    KEY_STATE = 'current'

    as_primary = Column(Boolean, default=False)
    as_oid = Column(Boolean, default=False)
    as_time = Column(Boolean, default=False)
    stateful = Column(Boolean, default=False)
    sorting = Column(VariableSorting, default=VariableSorting.none)
    category = Column(VariableCategory, default=VariableCategory.dependent)
    position = Column(Integer)
    values = Column(JSON)
    type_id = Column(Integer, ForeignKey('lambdas.id'))
    type_ = relationship('Lambda', foreign_keys=[type_id])

    def __init__(self, name, type_, description='', as_primary=None, as_oid=None, as_time=None, stateful=None,
                 category=VariableCategory.dependent, sorting=VariableSorting.none, values=None):
        """
        Construct the variable
        :param name: the name of the variable
        :type name: str
        :param type_: the type of the variable
        :type type_: Lambda
        :param description: the description of the variable
        :type description: str
        :param as_primary: whether the variable is a primary variable, i.e., used to generate oid
        :type as_primary: bool
        :param as_oid: whether the variable is treated as oid, i.e., _oid value is generated from this variable
        :type as_oid: bool
        :param as_time: whether the variable is treated as time, i.e., _timestamp is a copy of this variable
        :type as_time: bool
        :param stateful: whether the variable is stateful, default to False
        :type stateful: bool
        :param category: what kind of variable, ['dependent', 'internal', 'input', 'output', 'parameter']
        :type category: VariableCategory
        :param sorting: how to sort the objects according to the value of this variable, ['desc', 'asc', 'none']
        :type sorting: VariableSorting
        :param values: json object to store default and state values, e.g., {'default': 2, 'state': 3}
        :type values: dict
        """
        self.id = uuid_int()
        self.name = name or self.VAR_ANONYMOUS_STUB + random_name()
        self.type_ = type_
        self.description = description
        self.category = category
        self.as_primary = as_primary or (category is VariableCategory.input) or (category is VariableCategory.output)
        self.as_oid = as_oid or False
        self.as_time = as_time or False
        self.stateful = stateful or category is VariableCategory.parameter
        self.sorting = sorting
        self.values = values or {}

    def __repr__(self):
        return '{}: {}'.format(self.name, self.type_)

    def __str__(self):
        return self.__repr__()

    @property
    def default(self):
        return self.values.get(self.KEY_DEFAULT, None) or self.type_.default

    @property
    def value(self):
        return self.values.get(self.KEY_STATE, None) or self.default

    @value.setter
    def value(self, v):
        self.values[self.KEY_STATE] = v


lambda_variable = Table(
    'lambda_variable', metadata,
    Column('id', Integer, primary_key=True, default=uuid_int()),
    Column('lambda_id', Integer, ForeignKey('lambdas.id')),
    Column('variable_id', Integer, ForeignKey('variables.id')),
)


class Lambda(Model, AuditableMixin):
    """Lambda model is a function"""
    __tablename__ = 'lambdas'

    category = Column(String(64))

    VAR_LABEL = '_label'
    VAR_LABEL_T = 'float'
    VAR_OID = '_oid'
    VAR_OID_T = 'int64'
    VAR_PROB = '_prob'
    VAR_PROB_T = 'float'
    VAR_TIMESTAMP = '_timestamp'
    VAR_TIMESTAMP_T = 'datetime64[ns]'
    VAR_TOMBSTONE = '_tombstone'
    VAR_TOMBSTONE_T = 'bool'

    module_id = Column(Integer, ForeignKey(Module.id), nullable=False)
    module = relationship(Module, back_populates='lambdas')
    bindings = relationship(Variable, order_by=Variable.position, collection_class=ordering_list('position'),
                            secondary=lambda_variable)
    definition = Column(Text, default='')
    parent_id = Column(Integer, ForeignKey('lambdas.id'))
    children = relationship('Lambda', backref=backref('parent', remote_side=[id]))
    atomic = Column(Boolean, default=False)
    version = Column(String(32), default=new_version, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'lambda',
        'polymorphic_on': category,
        'with_polymorphic': '*'
    }

    def __init__(self, module=None, name='', description='', bindings=None, user=None):
        self.module: Module = module
        self.id: str = uuid_int()
        self.name: str = name
        self.description: str = description
        self.version: str = new_version()
        self.owner: User = user
        self.bindings: List[Variable] = bindings or []
        self.atomic: bool = False
        self.definition: str = ''
        self._data: DataFrame or None = None
        self.modified_or_new: bool = True

    @orm.reconstructor
    def init_on_load(self):
        self._data = None
        self.modified_or_new = False

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.signature

    def __hash__(self):
        if self.id is not None:
            return self.id
        h = 0
        if self.module:
            h += hash(self.module_id) << 7
        h += hash(self.name) << 7
        if self.version:
            h += hash(self.version)
        return h

    def __eq__(self, other):
        return self.__class__ is not other.__class__ and hash(self) == hash(other)

    def __contains__(self, item):
        if isinstance(item, Variable):
            return item.name in self._all_columns

        if isinstance(item, str):
            return item in self._all_columns

        return False

    def __call__(self, **kwargs):
        pass

    def _repr_html_(self):
        return self.data._repr_html_()

    @lazy_property
    def default(self):
        """
        The default value for the Lambda
        """
        return {v.name: v.default for v in self.bindings}

    @lazy_property
    def is_functional(self):
        """
        Whether the Lambda has any output variables
        :rtype: bool
        """
        return any(v.category is VariableCategory.output for v in self.bindings)

    @lazy_property
    def output_type(self):
        """
        Return the output type. If no output variable defined, return itself
        :return: the output type
        :rtype: Lambda
        """
        return tuple(v.type_ for v in self.bindings if v.category is VariableCategory.output) or self

    @lazy_property
    def oid_col(self):
        """
        Given oid column
        :return: the column name
        :rtype: str or None
        """
        for v in self.bindings:
            if v.as_oid:
                return v.name
        return None

    @lazy_property
    def time_col(self):
        """
        Given time column
        :return: the column name
        :rtype: str or None
        """
        for v in self.bindings:
            if v.as_time:
                return v.name
        return None

    @property
    def data(self):
        if self._data is None:
            if self.atomic:
                self._data = self.empty_data()
            else:
                self._data = self._load_data()
        return self._data

    @data.setter
    def data(self, value):
        if value is None:
            self._data = self.empty_data()
        else:
            self._data = value

    @property
    def signature(self):
        return self.module + '.' + self.name + '$' + self.version

    def clone(self):
        """
        Clone itself and bump up the version. Make sure updates are done after clone.
        :return: the cloned version of it
        :rtype: Lambda
        """
        lam = self.__class__(namespace=self.namespace, name=self.name, description=self.description,
                             params=self.params, variables=self.variables)
        lam.cloned_from = self
        lam.anchor = False
        lam.atomic = self.atomic
        lam.queryable = self.queryable
        lam.adaptable = self.adaptable
        if self._data is not None:
            lam._data = self._data
        return lam

    def _add_optional_variables(self, df):
        from norm.models.native import get_type_by_dtype
        current_variable_names = set(self._all_columns)
        vars_to_add = [Variable(col, get_type_by_dtype(dtype)) for col, dtype in zip(df.columns, df.dtypes)
                       if col not in current_variable_names]
        if len(vars_to_add) > 0:
            from norm.models.revision import AddVariableRevision
            self._add_revision(AddVariableRevision(vars_to_add, self))

    def revise(self, query, description, df, op):
        """
        Revise the Lambda by a given query and its result. If the query is an action, result is None.
        :param query: the given query string grounded with specific versions
        :type query: str
        :param description: the comment on the revision
        :type description: str
        :param df: the result data
        :type df: DataFrame
        :param op: the type of revision, conjunction or disjunction
        :type op: RevisionType
        :return: revised data or None
        :rtype: DataFrame
        """
        # If the query already exists, the revision is skipped
        if any((rev.query == query for rev in self.revisions)):
            return self.data.loc[df.index] if df is not None else None

        if df is not None and isinstance(df, DataFrame):
            assert(df.index.name == self.VAR_OID)
            assert(self.VAR_TIMESTAMP in df.columns)

            # Add new optional variables if the data contains variables that are not declared in this Lambda
            self._add_optional_variables(df)

            # Drop duplicated rows by the index
            delta = df[~df.index.duplicated(keep='first')]

            # Ensure the dtype and fill defaults
            for v in self.variables:
                if v.name in delta.columns:
                    try:
                        delta.loc[:, v.name] = v.type_.convert(delta[v.name])
                    except:
                        msg = '{} does not comply with the type {}'.format(v.name, v.type_)
                        logger.error(msg)
                        raise
        else:
            delta = None

        # Apply corresponding revisions
        from norm.models.revision import ConjunctionRevision, DisjunctionRevision
        if op == RevisionType.DISJUNCTION:
            self._add_revision(DisjunctionRevision(query, description, self, delta))
        elif op == RevisionType.CONJUNCTION:
            self._add_revision(ConjunctionRevision(query, description, self, delta))
        else:
            msg = 'Revision {} has not been implemented yet'.format(op)
            logger.error(msg)
            raise NotImplementedError(msg)

        # Enable queryable
        if not self.queryable:
            self.queryable = True

        return self.data.loc[df.index] if delta is not None else None

    def fit(self):
        """
        Fit the model with all the existing data or given data
        """
        from norm.models.revision import FitRevision
        # TODO: implement the query
        revision = FitRevision('', '', self)
        self._add_revision(revision)

    def fill_na(self, df):
        """
        Fill the null data with default values
        :param df: the data
        :type df: DataFrame
        :return: the filled DataFrame
        :rtype: DataFrame
        """
        df = self._fill_label(df)
        df = self._fill_prob(df)
        df = self._fill_tombstone(df)
        return df

    def fill_primary(self, df):
        for var in self.variables:
            if var.primary:
                if var.name in df.columns:
                    df.loc[:, var.name] = df[var.name].fillna(var.type_.default)
                else:
                    df[var.name] = var.type_.default
        return df

    def fill_oid(self, df):
        if df.index.name == self.VAR_OID:
            return df

        if self.VAR_OID in df.columns:
            return df.set_index(self.VAR_OID)

        # if OID column is given
        oid_col = self.oid_col
        if oid_col is not None and oid_col in df.columns:
            df[self.VAR_OID] = df[oid_col]
            df = df.set_index(self.VAR_OID)
            return df

        # if OID column is given but with no value in the data
        # primary columns are used to generate the oid and backfill it

        cols = [v.name for v in self.variables if v.primary and v.name in df.columns]
        c = None
        for col in cols:
            if c is None:
                c = df[col].astype(str)
            else:
                c = c.str.cat(df[col].astype(str))
        if c is not None:
            df[self.VAR_OID] = c.str.encode('utf-8').apply(zlib.adler32).astype('int64')
            df = df.set_index(self.VAR_OID)
        else:
            df.index.rename(self.VAR_OID, inplace=True)

        if oid_col is not None:
            df[oid_col] = df.index.values
        return df

    def fill_time(self, df):
        time_col = self.time_col

        if self.VAR_TIMESTAMP not in df.columns:
            if time_col is not None and time_col in df.columns:
                df[self.VAR_TIMESTAMP] = df[time_col].astype('datetime64[ns]')
            else:
                df[self.VAR_TIMESTAMP] = np.datetime64(datetime.utcnow())
        else:
            if time_col is not None and time_col in df.columns:
                df[self.VAR_TIMESTAMP].fillna(df[time_col].astype('datetime64[ns]'), inplace=True)
            else:
                df[self.VAR_TIMESTAMP].fillna(np.datetime64(datetime.utcnow()), inplace=True)
        return df

    def _fill_label(self, df):
        if self.VAR_LABEL not in df.columns:
            df[self.VAR_LABEL] = 1.0
        else:
            df[self.VAR_LABEL].fillna(1.0, inplace=True)
        return df

    def _fill_prob(self, df):
        if self.VAR_PROB not in df.columns:
            df[self.VAR_PROB] = 1.0
        else:
            df[self.VAR_PROB].fillna(1.0, inplace=True)
        return df

    def _fill_tombstone(self, df):
        if self.VAR_TOMBSTONE not in df.columns:
            df[self.VAR_TOMBSTONE] = False
        else:
            df[self.VAR_TOMBSTONE].fillna(False, inplace=True)
        return df

    def add_variable(self, variables):
        """
        Add new new variables to the Lambda
        :type variables: List[Variable] or Variable
        """
        if isinstance(variables, Variable):
            variables = [variables]
        if len(variables) == 0:
            return
        from norm.models.revision import AddVariableRevision
        revision = AddVariableRevision(variables, self)
        self._add_revision(revision)

    def delete_variable(self, names):
        """
        Delete variables from the Lambda
        :type names: List[str]
        """
        if len(names) == 0:
            return
        from norm.models.revision import DeleteVariableRevision
        revision = DeleteVariableRevision(names, self)
        self._add_revision(revision)

    def rename_variable(self, renames):
        """
        Change a variable name to another. The argument is a on keyword argument format. The key should exist in
        the Lambda and the value to be the target name.
        :type renames: Dict[str, str]
        """
        if len(renames) == 0:
            return
        from norm.models.revision import RenameVariableRevision
        revision = RenameVariableRevision(renames, self)
        self._add_revision(revision)

    def astype(self, variables):
        """
        Change the type of variables. The variable names to be changed should exist in current Lambda. The new types
        are specified in the variable type_ attribute.
        :type variables: List[Variable]
        """
        if len(variables) == 0:
            return
        from norm.models.revision import RetypeVariableRevision
        revision = RetypeVariableRevision(variables, self)
        self._add_revision(revision)

    def _add_revision(self, revision):
        revision.apply()
        self.current_revision += 1
        self.modified_or_new = True

    def save(self):
        """
        Save the current version
        """
        if not self.atomic:
            self._save_data()
        if self.adaptable:
            self._save_model()
        self.modified_or_new = False

    @property
    def _all_columns(self):
        return [self.VAR_OID, self.VAR_PROB, self.VAR_LABEL, self.VAR_TIMESTAMP,
                self.VAR_TOMBSTONE] + [v.name for v in self.variables]

    @property
    def _all_column_types(self):
        return [self.VAR_OID_T, self.VAR_PROB_T, self.VAR_LABEL_T, self.VAR_TIMESTAMP_T,
                self.VAR_TOMBSTONE_T] + [v.type_.dtype for v in self.variables]

    def empty_data(self):
        """
        Create an empty data frame
        :return: the data frame with columns
        :rtype: DataFrame
        """
        df = DataFrame(columns=self._all_columns)
        return df.astype(dict(zip(self._all_columns, self._all_column_types))).set_index(self.VAR_OID)

    def _load_data(self):
        """
        Load data if it exists. If the current version is not an anchor, the previous versions will be combined.
        :return: the combined data
        :rtype: DataFrame
        """
        if self._data is not None:
            return self._data

        if self.anchor:
            self._data = self.empty_data()
        elif self.cloned_from is None:
            msg = "Failed to find the anchor version. The chain is broken for {}".format(self)
            logger.error(msg)
            raise RuntimeError(msg)
        else:
            self._data = self.cloned_from._load_data()

        from norm.models.revision import DeltaRevision
        for i in range(self.current_revision + 1):
            revision = self.revisions[i]
            if isinstance(revision, DeltaRevision):
                revision.redo()

        # Choose the rows still alive and the columns specified in schema
        self._data = self._data[self._all_columns[1:]][~self._data[self.VAR_TOMBSTONE]]
        return self._data

    @_only_queryable
    def _save_data(self):
        """
        Save all revisions' data
        """
        if not os.path.exists(self.folder):
            self._create_folder()

        for revision in self.revisions:
            revision.save()

    @_only_adaptable
    def _build_model(self):
        """
        Build an adaptable model
        TODO: to implement
        """
        pass

    @_only_adaptable
    def _load_model(self):
        """
        Load an adapted model
        TODO: to implement
        :return:
        """
        pass

    @_only_adaptable
    def _save_model(self):
        """
        Save an adapted model
        TODO: to implement
        :return:
        """
        pass


def retrieve_type(namespaces, name, version=None, status=None):
    """
    Retrieving a Lambda
    :type namespaces: str, List[str] or None
    :type name: str
    :type version: str or None
    :type status: Status or None
    :return: the Lambda or None
    """
    from norm.config import session

    if version == '$lastest':
        version = None
    elif version == '$best':
        raise NotImplementedError('Select the version for the best is not implemented yet')

    queries = [Lambda.name == name]
    if status is not None and isinstance(status, Status):
        queries.append(Lambda.status == status)
    if namespaces is not None:
        if isinstance(namespaces, str):
            queries.append(Lambda.namespace == namespaces)
        else:
            queries.append(Lambda.namespace.in_(namespaces))
    if version is not None:
        queries.append(Lambda.version.startswith(version))

    lam = session.query(Lambda) \
                 .filter(*queries) \
                 .order_by(desc(Lambda.created_on)) \
                 .first()
    return lam



