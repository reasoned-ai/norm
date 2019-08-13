"""A collection of ORM sqlalchemy models for Lambda"""
import zlib

import norm.config as config
from norm.models.mixins import ParametrizedMixin, ARRAY, lazy_property
from norm.models.license import License
from norm.models.user import User
from norm.models import Model

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime, Enum, desc, UniqueConstraint, \
    orm, LargeBinary
from sqlalchemy import Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

import os
import errno
import enum

from datetime import datetime
from pandas import DataFrame
from hashids import Hashids
import numpy as np

from typing import List, Dict

import logging
logger = logging.getLogger(__name__)

metadata = Model.metadata
hashids = Hashids(min_length=config.VERSION_MIN_LENGTH)


class Variable(Model):
    """Variable placeholder"""

    __tablename__ = 'variables'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), default='')
    primary = Column(Boolean, default=False)
    as_oid = Column(Boolean, default=False)
    as_time = Column(Boolean, default=False)
    position = Column(Integer)
    type_id = Column(Integer, ForeignKey('lambdas.id'))
    type_ = relationship('Lambda', foreign_keys=[type_id])

    def __init__(self, name, type_, primary=False, as_oid=False, as_time=False):
        """
        Construct the variable
        :param name: the full name of the variable
        :type name: str
        :param type_: the type of the variable
        :type type_: Lambda
        :param primary: whether the variable is a primary for an Lambda
        :type primary: bool
        :param as_oid: whether the variable is treated as oid
        :type as_oid: bool
        :param as_time: whether the variable is treated as time
        :type as_time: bool
        """
        self.id = None
        self.name = name
        self.type_ = type_
        self.primary = primary
        self.as_oid = as_oid
        self.as_time = as_time

    def __hash__(self):
        return hash(self.name) + hash(self.type_)

    def __eq__(self, other):
        if other is None or not isinstance(other, Variable):
            return False
        return other.name == self.name and other.type_ == self.type_

    def __repr__(self):
        return '{}: {}'.format(self.name, self.type_)

    def __str__(self):
        return self.__repr__()


lambda_variable = Table(
    'lambda_variable', metadata,
    Column('id', Integer, primary_key=True),
    Column('lambda_id', Integer, ForeignKey('lambdas.id')),
    Column('variable_id', Integer, ForeignKey('variables.id')),
)


class Status(enum.Enum):
    """
    Indicate whether the lambda function can be modified or not
    """
    DRAFT = 0
    READY = 1


class RevisionType(enum.Enum):
    """
    Revision type
    """
    DISJUNCTION = 0
    CONJUNCTION = 1


def new_version():
    import time
    return '$' + hashids.encode(int(time.time() * 1000))


def _check_draft_status(func):
    """
    A decorator to check whether the current Lambda is in draft status
    :param func: a function to wrap
    :type func: Callable
    :return: a wrapped function
    :rtype: Callable
    """
    def wrapper(self, *args, **kwargs):
        if self.status != Status.DRAFT:
            msg = '{} is not in Draft status. Please clone first to modify'.format(self)
            logger.error(msg)
            raise RuntimeError(msg)
        return func(self, *args, **kwargs)
    return wrapper


def _only_queryable(func):
    """
    A decorator to bypass the function if the current Lambda is below queryable
    :param func: a function to wrap
    :type func: Callable
    :return: a wrapped function
    :rtype: Callable
    """
    def wrapper(self, *args, **kwargs):
        if not self.queryable:
            msg = '{} is not Queryable. Need to add data.'.format(self)
            logger.error(msg)
            raise RuntimeError(msg)
        return func(self, *args, **kwargs)
    return wrapper


def _only_adaptable(func):
    """
    A decorator to bypass the function if the current Lambda is below adaptable
    :param func: a function to wrap
    :type func: Callable
    :return: a wrapped function
    :rtype: Callable
    """
    def wrapper(self, *args, **kwargs):
        if not self.adaptable:
            msg = '{} is not adaptable. Need to add probabilistic lambdas.'.format(self)
            logger.error(msg)
            raise RuntimeError(msg)
        return func(self, *args, **kwargs)
    return wrapper


class Namespace(Model, ParametrizedMixin):
    """Namespace"""
    __tablename__ = 'namespace'
    id = Column(Integer, primary_key=True)
    name = Column(String(512), default='')
    description = Column(Text, default='')
    created_by_id = Column(Integer, ForeignKey(User.id))
    owner = relationship(User, backref='namespaces', foreign_keys=[created_by_id])
    created_on = Column(DateTime, default=datetime.now)
    changed_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    secret = Column(LargeBinary, default=b'')


class Lambda(Model, ParametrizedMixin):
    """Lambda model is a function"""
    __tablename__ = 'lambdas'
    category = Column(String(128))

    VAR_OUTPUT = '_output'
    # OUTPUT default to the OID, hence the type is integer
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
    VAR_ANONYMOUS_STUB = 'var'

    # identifiers
    id = Column(Integer, primary_key=True)
    namespace = Column(String(512), default='')
    name = Column(String(256), nullable=False)
    # data type
    dtype = Column(String(16), default='object')
    # computational properties
    atomic = Column(Boolean, default=False)
    queryable = Column(Boolean, default=False)
    adaptable = Column(Boolean, default=False)
    # owner
    created_by_id = Column(Integer, ForeignKey(User.id))
    owner = relationship(User, backref='lambdas', foreign_keys=[created_by_id])
    # audition
    created_on = Column(DateTime, default=datetime.now)
    changed_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # schema
    description = Column(Text, default='')
    variables = relationship(Variable, order_by=Variable.position, collection_class=ordering_list('position'),
                             secondary=lambda_variable)
    # version
    anchor = Column(Boolean, default=True)
    cloned_from_id = Column(Integer, ForeignKey('lambdas.id'))
    cloned_from = relationship('Lambda', remote_side=[id])
    merged_from_ids = Column(ARRAY(Integer))
    version = Column(String, default=new_version, nullable=False)
    # revision
    revisions = relationship('Revision', order_by='Revision.position', collection_class=ordering_list('position'))
    current_revision = Column(Integer, default=-1)
    status = Column(Enum(Status), default=Status.DRAFT)
    # license
    license_id = Column(Integer, ForeignKey(License.id))
    license = relationship(License, foreign_keys=[license_id])

    __mapper_args__ = {
        'polymorphic_identity': 'lambda',
        'polymorphic_on': category,
        'with_polymorphic': '*'
    }

    __table_args__ = tuple(UniqueConstraint('namespace', 'name', 'version', name='unique_lambda'))

    def __init__(self, namespace='', name='', description='', params='{}', variables=None, dtype=None, user=None):
        self.id: int = None
        self.namespace: str = namespace
        self.name: str = name
        self.version: str = new_version()
        self.description: str = description
        self.params: str = params
        self.owner: User = user
        self.status: Status = Status.DRAFT
        self.merged_from_ids: List[int] = []
        self.variables: List[Variable] = variables or []
        from norm.models.revision import Revision
        self.revisions: List[Revision] = []
        self.current_revision: int = -1
        self.dtype: str = dtype or 'object'
        self.anchor: bool = True
        self.atomic: bool = False
        self.queryable: bool = False
        self.adaptable: bool = False
        self._data: DataFrame = None
        self.modified_or_new = True
        self.license_id = 0

    @orm.reconstructor
    def init_on_load(self):
        self._data = None
        self.modified_or_new = False

    @hybrid_property
    def nargs(self):
        return len(self.variables)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.signature

    def __hash__(self):
        if self.id is not None:
            return self.id
        h = 0
        if self.namespace:
            h += hash(self.namespace) << 7
        h += hash(self.name) << 7
        if self.version:
            h += hash(self.version)
        return h

    def __eq__(self, other):
        if not isinstance(other, Lambda):
            return False

        return hash(self) == hash(other)

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

    @classmethod
    def exists(cls, session, obj):
        """
        Build the SQLAlchemy equality condition
        :param session: the session to check against
        :type session: sqlalchemy.orm.Session
        :param obj: another Lambda to compare with
        :type obj: Lambda
        :return: List
        """
        in_stores = session.query(Lambda)\
                           .filter(Lambda.name == obj.name,
                                   Lambda.description == obj.description,
                                   Lambda.namespace == obj.namespace)\
                           .all()
        return any(in_store.variables == obj.variables for in_store in in_stores)

    @property
    def default(self):
        """
        The default value for the Lambda
        """
        return {v.name: v.type_.default for v in self.variables}

    @property
    def is_functional(self):
        """
        Whether the Lambda is in the relational or functional format
        :rtype: bool
        """
        return len(self.variables) > 0 and self.variables[-1].name == self.VAR_OUTPUT

    @property
    def output_type(self):
        """
        Return the output type. If no output variable defined, return itself
        :return: the output type
        :rtype: Lambda
        """
        if self.is_functional:
            return self.variables[-1].type_
        else:
            return self

    @lazy_property
    def oid_col(self):
        """
        Given oid column
        :return: the column name
        :rtype: str or None
        """
        for v in self.variables:
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
        for v in self.variables:
            if v.as_time:
                return v.name
        return None

    def get_type(self, variable_name):
        """
        Get the type of the variable by the name
        :param variable_name: the name of the variable
        :type variable_name: str
        :return: the type of that variable
        :rtype: Lambda
        """
        if variable_name == self.VAR_OUTPUT and not self.is_functional:
            return self
        elif variable_name == self.VAR_OID:
            return self.VAR_OID_T
        elif variable_name == self.VAR_TIMESTAMP:
            return self.VAR_TIMESTAMP_T
        elif variable_name == self.VAR_PROB:
            return self.VAR_PROB_T
        elif variable_name == self.VAR_LABEL:
            return self.VAR_LABEL_T
        elif variable_name == self.VAR_TOMBSTONE:
            return self.VAR_TOMBSTONE_T

        for v in self.variables:
            if v.name == variable_name:
                return v.type_
        return None

    @property
    def data(self):
        if self._data is None:
            if self.queryable:
                self._data = self._load_data()
            else:
                self._data = self.empty_data()
        return self._data

    @data.setter
    def data(self, value):
        if value is None:
            self._data = self.empty_data()
        else:
            self._data = value

    @property
    def signature(self):
        if self.namespace is not None and self.namespace.strip() != '':
            return self.namespace + '.' + self.name + self.version[:config.VERSION_MIN_LENGTH]
        else:
            return self.name + self.version[:config.VERSION_MIN_LENGTH]

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

    def merge(self, others):
        """
        Clone itself and merge several other versions into the new version
        :param others: other versions
        :type others: List[Lambda]
        :return: the merged version
        :rtype: Lambda
        """
        assert(all([o.namespace == self.namespace and o.name == self.name for o in others]))

        lam = self.clone()
        lam.merged_from_ids = [o.id for o in others]
        for o in others:
            lam.revisions.extend(o.revisions)
        while not self.end_of_revisions:
            self.forward()
        lam.status = Status.READY
        return lam

    def compact(self):
        """
        Compact this version with previous versions to make an anchor version
        :return:
        TODO: to implement
        """
        pass

    def _add_optional_variables(self, df):
        from norm.models.native import get_type_by_dtype
        current_variable_names = set(self._all_columns)
        vars_to_add = [Variable(col, get_type_by_dtype(dtype)) for col, dtype in zip(df.columns, df.dtypes)
                       if col not in current_variable_names]
        if len(vars_to_add) > 0:
            from norm.models.revision import AddVariableRevision
            self._add_revision(AddVariableRevision(vars_to_add, self))

    @_check_draft_status
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

    @_check_draft_status
    @_only_adaptable
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

    @_check_draft_status
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

    @_check_draft_status
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

    @_check_draft_status
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

    @_check_draft_status
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

    @_check_draft_status
    def save(self):
        """
        Save the current version
        """
        if self.queryable:
            self._save_data()
        if self.adaptable:
            self._save_model()
        self.modified_or_new = False

    @_check_draft_status
    def remove_revisions(self):
        for rev in self.revisions:
            rev.undo()
        self.current_revision = -1
        self.revisions = []

    @property
    def empty_revisions(self):
        return len(self.revisions) == 0

    @property
    def end_of_revisions(self):
        return self.current_revision == len(self.revisions) - 1

    @property
    def begin_of_revisions(self):
        return self.current_revision == -1

    @_check_draft_status
    def rollback(self):
        """
        Rollback to the previous revision if it is in draft status
        """
        if 0 <= self.current_revision < len(self.revisions):
            self.revisions[self.current_revision].undo()
            self.current_revision -= 1
        else:
            if self.current_revision == -1:
                msg = '{} has already rolled back to the beginning of the version.\n ' \
                      'Might want to rollback the version'.format(self)
                logger.warning(msg)
            else:
                msg = 'Current revision {} is higher than it has {}'.format(self.current_revision, len(self.revisions))
                logger.error(msg)
                raise RuntimeError(msg)

    @_check_draft_status
    def forward(self):
        """
        Forward to the next revision if it is in draft status
        """
        if self.current_revision < len(self.revisions) - 1:
            self.revisions[self.current_revision + 1].redo()
            self.current_revision += 1
        else:
            if self.current_revision == len(self.revisions) - 1:
                msg = '{} is already at the latest revision.\n ' \
                      'Might want to forward the version'.format(self)
                logger.warning(msg)
            else:
                msg = 'Current revision {} is higher than it has {}'.format(self.current_revision, len(self.revisions))
                logger.error(msg)
                raise RuntimeError(msg)

    @property
    def folder(self):
        return '{}/{}/{}/{}'.format(config.DATA_STORAGE_ROOT,
                                    self.namespace.replace('.', '/'),
                                    self.name,
                                    self.version)

    @_only_queryable
    def _create_folder(self):
        """
        Create the folder for the namespace.
        """
        # TODO: abstract the data storage folder creation
        try:
            # for the case of concurrent processing
            os.makedirs(self.folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                msg = 'Can not create the folder {}'.format(self.folder)
                logger.error(msg)
                logger.error(str(e))
                raise e

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

    @_only_queryable
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



