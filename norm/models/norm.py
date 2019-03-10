"""A collection of ORM sqlalchemy models for Lambda"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import os
import errno
import uuid

from datetime import datetime
import enum

from future.standard_library import install_aliases

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime, Enum, desc, UniqueConstraint, orm
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, with_polymorphic, joinedload
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import lazyload
from flask_sqlalchemy_cache import FromCache
from flask_sqlalchemy_cache import RelationshipCache

from norm.models.mixins import lazy_property, ParametrizedMixin, new_version
from norm.models.license import License
from norm.utils import current_user
import norm.config as config

from pandas import DataFrame
import pandas as pd
import numpy as np

from typing import List, Dict

import logging
logger = logging.getLogger(__name__)

install_aliases()

Model = config.Model
metadata = Model.metadata
user_model = config.user_model
cache = config.cache


class Variable(Model, ParametrizedMixin):
    """Variable placeholder"""

    __tablename__ = 'variables'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), default='')
    type_id = Column(Integer, ForeignKey('lambdas.id'))
    type_ = relationship('Lambda', foreign_keys=[type_id])

    def __init__(self, name, type_):
        """
        Construct the variable
        :param name: the full name of the variable
        :type name: str
        :param type_: the type of the variable
        :type type_: Lambda
        """
        self.id = None
        self.name = name
        self.type_ = type_

    def __hash__(self):
        return hash(self.name) + hash(self.type_)

    def __eq__(self, other):
        if other is None or not isinstance(other, Variable):
            return False
        return other.name == self.name and other.type_ == self.type_


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


class Level(enum.IntEnum):
    """
    Different computational level for Lambda functions:
        1. any function that can compute the outputs given inputs is at level computable.
        2. any function that can record the input-output as data such that a query can search through data to provide
           statistics and aggregations is at level queryable.
        3. any function that can adapt the parameters by fitting the recorded input-output data with respect to a
           certain objective function.
    """
    COMPUTABLE = 0
    QUERYABLE = 1
    ADAPTABLE = 2


def default_version(context):
    params = context.get_current_parameters()
    namespace = params['namespace']
    name = params['name']
    return new_version(namespace, name)


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
        if self.level < Level.QUERYABLE:
            return
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
        if self.level < Level.ADAPTABLE:
            return
        return func(self, *args, **kwargs)
    return wrapper


class Lambda(Model, ParametrizedMixin):
    """Lambda model is a function"""
    __tablename__ = 'lambdas'
    category = Column(String(128))

    VAR_OUTPUT = 'output'
    VAR_LABEL = 'label'
    VAR_LABEL_T = 'float'
    VAR_OID = 'oid'
    VAR_OID_T = 'object'
    VAR_PROB = 'prob'
    VAR_PROB_T = 'float'
    VAR_TIMESTAMP = 'timestamp'
    VAR_TIMESTAMP_T = 'datetime64[ns]'
    VAR_TENSOR = 'tensor'
    VAR_TOMBSTONE = 'tombstone'
    VAR_TOMBSTONE_T = 'bool'

    # identifiers
    id = Column(Integer, primary_key=True, autoincrement=True)
    namespace = Column(String(512), default='')
    name = Column(String(256), nullable=False)
    # data type
    dtype = Column(String(16), default='object')
    # tensor type and shape
    ttype = Column(String(16), default='float32')
    shape = Column(ARRAY(Integer), default=[100])
    # complexity level
    level = Column(Enum(Level), default=Level.COMPUTABLE)
    # owner
    created_by_id = Column(Integer, ForeignKey(user_model.id))
    owner = relationship(user_model, backref='lambdas', foreign_keys=[created_by_id])
    # audition
    created_on = Column(DateTime, default=datetime.now)
    changed_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # schema
    description = Column(Text, default='')
    variables = relationship(Variable, secondary=lambda_variable)
    # version
    anchor = Column(Boolean, default=True)
    cloned_from_id = Column(Integer, ForeignKey('lambdas.id'))
    cloned_from = relationship('Lambda', remote_side=[id])
    merged_from_ids = Column(ARRAY(Integer))
    version = Column(Integer, default=default_version, nullable=False)
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

    def __init__(self, namespace='', name='', description='', params='{}', variables=None, dtype=None, ttype=None,
                 shape=None):
        self.id = None  # type: int
        self.namespace = namespace  # type: str
        self.name = name  # type: str
        self.version = None  # type: int
        self.description = description   # type: str
        self.params = params  # type: str
        self.owner = current_user()  # type: user_model
        self.status = Status.DRAFT  # type: Status
        self.merged_from_ids = []  # type: List[int]
        self.variables = variables or []  # type: List[Variable]
        self.revisions = []  # type: List[Revision]
        self.current_revision = -1  # type: int
        self.dtype = dtype or 'object'   # type: str
        self.ttype = ttype or 'float32'  # type: str
        self.shape = shape or [100]  # type: List[int]
        self.anchor = True  # type: bool
        self.level = Level.COMPUTABLE  # type: Level
        self.df = None  # type: DataFrame

    @orm.reconstructor
    def init_on_load(self):
        self.df = None

    @hybrid_property
    def nargs(self):
        return len(self.variables)

    @hybrid_property
    def dim(self):
        return len(self.shape)

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

    def get_type(self, variable_name):
        """
        Get the type of the variable by the name
        :param variable_name: the name of the variable
        :type variable_name: str
        :return: the type of that variable
        :rtype: Lambda
        """
        for v in self.variables:
            if v.name == variable_name:
                return v.type_
        return None

    @property
    def data(self):
        if self.df is None:
            self.df = self.from_cache()
        if self.df is None:
            self.df = self.empty_data()
        return self.df

    @property
    def signature(self):
        if self.namespace:
            return '@'.join((self.namespace + '.' + self.name, str(self.version)))
        else:
            return '@'.join((self.name, str(self.version)))

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
        lam.level = self.level
        if self.df is not None:
            lam.df = self.df.copy(False)
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

    @_check_draft_status
    def conjunction(self):
        """
        Revise with conjunction (AND)
        """
        from norm.models.revision import ConjunctionRevision
        # TODO: implement the query
        revision = ConjunctionRevision('', '', self)
        self._add_revision(revision)

    @_check_draft_status
    def disjunction(self):
        """
        Revise with disjunction (OR)
        """
        from norm.models.revision import DisjunctionRevision
        # TODO: implement the query
        revision = DisjunctionRevision('', '', self)
        self._add_revision(revision)

    def fit(self):
        """
        Fit the model with all the existing data
        """
        from norm.models.revision import FitRevision
        # TODO: implement the query
        revision = FitRevision('', '', self)
        self._add_revision(revision)

    def _add_data(self, query, df):
        cols = {col: dtype for col, dtype in zip(df.columns, df.dtypes)}
        #for v in self.variables:
        #    assert(cols.get(v.name, v.type_.dtype) == v.type_.dtype)

        from norm.models.native import get_type_by_dtype
        current_variable_names = set(self._all_columns)
        vars_to_add = [Variable(col, get_type_by_dtype(dtype)) for col, dtype in cols.items()
                       if col not in current_variable_names]
        if len(vars_to_add) > 0:
            from norm.models.revision import AddVariableRevision
            self._add_revision(AddVariableRevision(vars_to_add, self))
        from norm.models.revision import DisjunctionRevision
        added_data = DisjunctionRevision(query, 'Append new data', self)
        added_data.delta = df
        self._add_revision(added_data)
        self.level = Level.QUERYABLE

    @_check_draft_status
    def read_csv(self, path, params):
        """
        Read data from a file
        :param path: the path to the data file
        :type path: str
        :param params: the parameters for reading csv
        :type params: Dict
        """
        if params is not None and isinstance(params, dict):
            df = pd.read_csv(path, **params)
        else:
            params = {}
            df = pd.read_csv(path)
        query = 'read("{}", {}, "csv")'.format(path, ', '.join('{}={}'.format(key, value)
                                                               for key, value in params.items()))
        self._add_data(query, df)

    @_check_draft_status
    def read_parquet(self, path, params):
        if params is not None and isinstance(params, dict):
            df = pd.read_parquet(path, **params)
        else:
            params = {}
            df = pd.read_parquet(path)
        query = 'read("{}", {}, "parq")'.format(path, ', '.join('{}={}'.format(key, value)
                                                                for key, value in params.items()))
        self._add_data(query, df)

    @_check_draft_status
    def read_jsonl(self, path):
        import os
        logger.error(os.getcwd())
        with open(path) as f:
            df = DataFrame([json.loads(line) for line in f])
        query = 'read("{}", "jsonl")'.format(path)
        self._add_data(query, df)

    @_check_draft_status
    def add_variable(self, variables):
        """
        Add new new variables to the Lambda
        :type variables: Tuple[Variable]
        """
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
        self.revisions.append(revision)
        revision.apply()
        self.current_revision += 1
        self.to_cache()

    def from_cache(self):
        """
        Retrieve the data from the cache if available
        :return: the data
        :rtype: DataFrame
        """
        if cache is None:
            return

        key = (self.id, self.current_revision)
        return cache.get(key)

    def to_cache(self):
        """
        Cache the data frame if cache is available
        """
        if cache is None or self.df is None:
            return

        key = (self.id, self.current_revision)
        cache.set(key, self.df)

    @_check_draft_status
    def save(self):
        """
        Save the current version
        """
        self._save_data()
        self._save_model()

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
        return '{}/{}/{}'.format(config.DATA_STORAGE_ROOT,
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
    def _tensor_columns(self):
        return ['{}_{}'.format(self.VAR_TENSOR, i) for i in range(int(np.prod(self.shape)))]

    @property
    def _all_columns(self):
        return [self.VAR_OID, self.VAR_PROB, self.VAR_LABEL, self.VAR_TIMESTAMP,
                self.VAR_TOMBSTONE] + self._tensor_columns + [v.name for v in self.variables]

    @property
    def _all_column_types(self):
        return [self.VAR_OID_T, self.VAR_PROB_T, self.VAR_LABEL_T, self.VAR_TIMESTAMP_T,
                self.VAR_TOMBSTONE_T] + [self.ttype] * len(self._tensor_columns) + \
               [v.type_.dtype for v in self.variables]

    def empty_data(self):
        """
        Create an empty data frame
        :return: the data frame with columns
        :rtype: DataFrame
        """
        df = DataFrame(columns=self._all_columns)
        return df.astype(dict(zip(self._all_columns, self._all_column_types)))

    @_only_queryable
    def _load_data(self):
        """
        Load data if it exists. If the current version is not an anchor, the previous versions will be combined.
        :return: the combined data
        :rtype: DataFrame
        """
        if self.df is not None:
            return self.df

        if self.anchor:
            self.df = self.empty_data()
        elif self.cloned_from is None:
            msg = "Failed to find the anchor version. The chain is broken for {}".format(self)
            logger.error(msg)
            raise RuntimeError(msg)
        else:
            self.df = self.cloned_from._load_data().copy(False)

        from norm.models.revision import DeltaRevision
        for i in range(self.current_revision + 1):
            revision = self.revisions[i]
            if isinstance(revision, DeltaRevision):
                revision.redo()

        # Choose the rows still alive and the columns specified in schema
        self.df = self.df[self._all_columns][~self.df[self.VAR_TOMBSTONE]]
        return self.df

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

    @_only_queryable
    def query(self, inputs, outputs):
        """
        Query the Lambda according to the inputs, and generate another Lambda projected to the outputs
        :param inputs: the inputs for variable and value pairs, or a query string
        :type inputs: Dict[str, Lambda] or str
        :param outputs: the outputs
        :type outputs: Dict[str, str]
        :return: the resulting view of the data
        :rtype: Lambda
        """
        output_name = outputs.get(self.VAR_OUTPUT, None) or str(uuid.uuid4())
        rt = Lambda(self.namespace, output_name)
        rt.level = self.level
        rt.status = Status.DRAFT
        if isinstance(inputs, str):
            # a query string passed in
            if inputs.find('.str.') > -1:
                rt.df = self.data.query(inputs, engine='python')
            else:
                rt.df = self.data.query(inputs)
        else:
            # TODO: execute the correct revisions according to the inputs and outputs.
            pass
        if outputs is not None and len(outputs) > 0:
            rt.variables = self.variables
            # TODO: fix this
            ocols = list(outputs.keys())
            rt.df = rt.df[ocols].rename(columns=outputs)
        return rt

    def __add__(self, other):
        assert(other, Lambda)
        return 3


class GroupLambda(Lambda):

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_group'
    }

    def all(self):
        """
        Combine the groups as columns
        :return: Lambda
        """
        raise NotImplementedError

    def any(self):
        """
        Combine the groups as concatenation
        :return: Lambda
        """
        raise NotImplementedError


class KerasLambda(Lambda):

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_keras'
    }

    @lazy_property
    def keras_model(self):
        return None

    def __call__(self, *args, **kwargs):
        """
        TODO: implement
        """
        pass


def retrieve_type(namespaces, name, version=None, status=None, session=None):
    """
    Retrieving a Lambda
    :type namespaces: str, List[str] or None
    :type name: str
    :type version: int or None
    :type status: Status or None
    :type session: sqlalchemy.orm.Session
    :return: the Lambda or None
    """
    #  find the latest versions
    queries = [Lambda.name == name]
    if status is not None and isinstance(status, Status):
        queries.append(Lambda.status == status)
    if namespaces is not None:
        if isinstance(namespaces, str):
            queries.append(Lambda.namespace == namespaces)
        else:
            queries.append(Lambda.namespace.in_(namespaces))
    if version is not None and isinstance(version, int):
        queries.append(Lambda.version <= version)

    if session is None:
        from norm.config import db
        session = db.session
    vc = RelationshipCache(Lambda.variables, cache)
    oc = RelationshipCache(Lambda.owner, cache)
    lc = RelationshipCache(Lambda.license, cache)
    cc = RelationshipCache(Lambda.cloned_from, cache)
    rc = RelationshipCache(Lambda.revisions, cache)
    lams = session.query(Lambda) \
                  .options(FromCache(cache)) \
                  .options(joinedload(Lambda.variables), oc) \
                  .options(joinedload(Lambda.owner), vc) \
                  .options(joinedload(Lambda.license), lc) \
                  .options(joinedload(Lambda.cloned_from), cc) \
                  .options(joinedload(Lambda.revisions), rc) \
                  .filter(*queries) \
                  .order_by(desc(Lambda.version)) \
                  .all()
    if len(lams) == 0:
        return None

    lam = lams[0]  # type: Lambda
    if version is not None and lam.version < version:
        msg = 'The specified version {} does not exist for {}.{}'.format(version, lam.namespace, lam.name)
        raise RuntimeError(msg)

    assert(lam is None or isinstance(lam, Lambda))
    return lam


def retrieve_variable(name, type_id, session=None):
    """
    Retrieving the variable by the name and the type id
    :type name: str
    :type type_id: int
    :type session: sqlalchemy.orm.Session or None
    :rtype: Variable or None
    """
    #  find the latest versions
    if session is None:
        from norm.config import db
        session = db.session

    vt = RelationshipCache(Variable.type_, cache)
    var = session.query(Variable)\
                 .options(FromCache(cache))\
                 .options(joinedload(Variable.type_), vt)\
                 .filter(Variable.name == name,
                         Variable.type_id == type_id)\
                 .first()
    return var
