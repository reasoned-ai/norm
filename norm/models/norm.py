"""A collection of ORM sqlalchemy models for Lambda"""
import logging
import os
import zlib
from datetime import datetime
from textwrap import dedent, indent
from typing import Dict
from typing import List

import numpy as np
from pandas import DataFrame
from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy import String, Boolean, orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

from norm.models import Model, SEPARATOR, Registrable, ModelError, store
from norm.models.license import License
from norm.models.mixins import AuditableMixin
from norm.models.mixins import lazy_property
from norm.models.variable import Variable, Output, Input, Parameter, Parent
from norm.utils import uuid_int, new_version, local_url

logger = logging.getLogger(__name__)

metadata = Model.metadata


class Module(Model, Registrable):
    """Module is a Norm namespace"""
    __tablename__ = 'modules'

    category = Column(String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'module',
        'polymorphic_on': category,
        'with_polymorphic': '*'
    }

    id = Column(Integer, primary_key=True, default=uuid_int)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, default='')
    url = Column(String(256))
    lambdas = relationship("Lambda", back_populates="module")
    license_id = Column(Integer, ForeignKey(License.id))
    license = relationship(License, foreign_keys=[license_id])
    script = Column(Text)

    created_on = Column(DateTime, default=datetime.utcnow)
    changed_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, script=None, description=None, url=None):
        self.id: int = uuid_int()
        self.script: str = script or ''
        self.name: str = name
        self.url: str = url or local_url(name, SEPARATOR)
        self.lambdas: List["Lambda"] = []
        self.license: License = store.license.MIT
        if description:
            self.description = description
        else:
            self.description_from_script()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name

    def __hash__(self):
        if self.id is not None:
            return self.id
        return hash(self.name)

    def __eq__(self, other):
        return self.__class__ is not other.__class__ and hash(self) == hash(other)

    def set_script(self, script):
        self.script = script
        self.description_from_script()

    def description_from_script(self):
        script = self.script
        if not script:
            return

        lines = script.strip(' ').split('/n')
        if lines[0].startswith(('"""', "'''")):
            description = []
            for line in lines[1:]:
                description.append(line)
                if line.endswith(('"""', "'''")):
                    break
            if not description[-1].endswith(('"""', "'''")):
                msg = f'{script} does not close the multi-line comments'
                raise ModelError(msg)
            self.description = ''.join(description)

    def exists(self):
        return [Module.name == self.name]


class Lambda(Model, AuditableMixin):
    """Lambda models a relation in Norm"""

    __tablename__ = 'lambdas'

    category = Column(String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'lambda',
        'polymorphic_on': category,
        'with_polymorphic': '*'
    }

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
    bindings = relationship(Variable, order_by=Variable.position, collection_class=ordering_list('position'))
    definition = Column(Text, default='')
    atomic = Column(Boolean, default=False)

    def __init__(self, module=None, name='', description='', version='', atomic=False, bindings=None):
        """
        :type module: Module
        :type name: str
        :type description: str
        :type version: str
        :type atomic: bool
        :type bindings: List[Variable]
        """
        self.module: Module = module
        self.id: int = uuid_int()
        self.name: str = name
        self.description: str = description
        self.version: str = version or new_version()
        self.bindings: List[Variable] = bindings or []
        self.atomic: bool = atomic
        self.definition: str = ''
        self._data: DataFrame or None = None
        if self.bindings:
            for v in self.bindings:
                v.scope = self

    @orm.reconstructor
    def init_on_load(self):
        self._data = None

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
        return any(isinstance(v, Output) for v in self.bindings)

    @lazy_property
    def output_type(self):
        """
        Return the output type. If no output variable defined, return itself
        :return: the output type
        :rtype: Tuple[Lambda]
        """
        return tuple(v.type_ for v in self.bindings if isinstance(v, Output)) or self

    @lazy_property
    def oid_col(self):
        """
        Given oid column
        :return: the column name
        :rtype: str or None
        """
        for v in self.bindings:
            if isinstance(v, Input) and v.as_oid:
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
            if isinstance(v, Input) and v.as_time:
                return v.name
        return None

    @lazy_property
    def declared_bindings(self):
        return [v for v in self.bindings if isinstance(v, (Parent, Input, Output, Parameter))]

    @lazy_property
    def input_variables(self):
        variables = []
        for v in self.bindings:
            if isinstance(v, Parent):
                variables.extend(v.type_.inputs)
            elif isinstance(v, (Input, Parameter)):
                variables.append(v)
        return variables

    @lazy_property
    def output_variables(self):
        return [v for v in self.bindings if isinstance(v, Output)]

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
        return f"{self.module}.{self.name}${self.version}"

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

    def _save_data(self):
        """
        Save all revisions' data
        """
        if not os.path.exists(self.folder):
            self._create_folder()

        for revision in self.revisions:
            revision.save()

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


class PythonLambda(Lambda):

    python_version = Column(String(8), default='3.7')
    python_packages = Column(Text, default='')

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_python'
    }

    def __init__(self, name, description, code='', python_version='3.7', module=None, version=None, atomic=True,
                 bindings=None):
        """
        Python function, inputs are wrapped into one variable, outputs are one variable too.
        :type name: str
        :type description: str
        :type code: str
        :type python_version: str
        :type module: norm.models.norm.Module
        :type version: str
        :type atomic: bool
        :type bindings: List[Variable]
        """
        super().__init__(name=name,
                         description=description,
                         module=module,
                         version=version,
                         atomic=atomic,
                         bindings=bindings)
        self.define(code)
        self.python_version = python_version

    def define(self, code):
        """
        :type code: str
        """
        self.definition = dedent(code).strip(' \n')

    def decorated(self):
        """
        Decorate code with a function definition
        """
        stmts = self.definition.split('\n')
        if not stmts[-1].startswith('return'):
            stmts[-1] = 'return ' + stmts[-1]
            script = indent('\n'.join(stmts), prefix='  ')
        else:
            script = indent(self.definition, prefix='  ')

        return "def func(" + ",".join(v.name for v in self.input_variables) + "):\n" + script + "\n"

    @lazy_property
    def func(self):
        try:
            d = {}
            exec(self.decorated(), d)
            return d.get('func')
        except Exception:
            msg = 'Can not load the python code: \n{}'.format(self.definition)
            raise ModelError(msg)


class SQLLambda(Lambda):

    sql_url = Column(String(128), default='')

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_sql'
    }

    def __init__(self, name, description, code='', sql_url='', module=None, version=None, atomic=True, bindings=None):
        """
        SQL function, inputs are wrapped into one variable, outputs are one variable too.
        :type name: str
        :type description: str
        :type code: str
        :type sql_url: str
        :type module: norm.models.norm.Module
        :type version: str
        :type atomic: bool
        :type bindings: List[Variable]
        """
        super().__init__(name=name,
                         description=description,
                         module=module,
                         version=version,
                         atomic=atomic,
                         bindings=bindings)
        self.definition = dedent(code).strip(' \n')
        self.sql_url = sql_url




