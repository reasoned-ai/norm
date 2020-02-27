"""A collection of ORM sqlalchemy models for Lambda"""
import logging
import os
import zlib
from datetime import datetime
from textwrap import dedent, indent
from typing import Dict, List, Any

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
from norm.models.variable import Variable, Output, Input, Parameter, Parent, Internal, External
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
    adapted = Column(Boolean, default=False)
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
            return item.name in self._schema_names

        if isinstance(item, str):
            return item in self._schema_names

        return False

    def get(self, item):
        """
        The variable to get
        :param item: the attribute name
        :type item: str
        :return: the variable
        :rtype: Variable or None
        """
        for b in self.bindings:
            if b.name == item:
                return b
        return None

    @lazy_property
    def _schema_names(self):
        """
        :return: the input/output variable names
        :rtype: List[str]
        """
        return [self.VAR_OID, self.VAR_TIMESTAMP, self.VAR_LABEL, self.VAR_PROB] +\
               [v.name for v in self.inputs + self.outputs]

    @lazy_property
    def _schema_dtypes(self):
        """
        :return: the dtypes for input/output variables
        :rtype: Dict[str, str]
        """
        dtypes = dict((v.name, v.dtype) for v in self.inputs + self.outputs)
        dtypes[self.VAR_OID] = self.VAR_OID_T
        dtypes[self.VAR_TIMESTAMP] = self.VAR_TIMESTAMP_T
        dtypes[self.VAR_LABEL] = self.VAR_LABEL_T
        dtypes[self.VAR_PROB] = self.VAR_PROB_T
        return dtypes

    @lazy_property
    def parents(self):
        """
        :return: Parent variables
        :rtype: List[Variable]
        """
        return [v for v in self.bindings if isinstance(v, Parent)]

    @lazy_property
    def inputs(self):
        """
        :return: Input variables
        :rtype: List[Input]
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
    def outputs(self):
        """
        :return: Output variables
        :rtype: List[Output]
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
    def internals(self):
        """
        :return: Internal variables
        :rtype: List[Internal]
        """
        return [v for v in self.bindings if isinstance(v, Internal)]

    @lazy_property
    def externals(self):
        """
        :return: External variables
        :rtype: List[External]
        """
        return [v for v in self.bindings if isinstance(v, External)]

    @lazy_property
    def parameters(self):
        """
        :return: Parameter variables
        :rtype: List[Parameter]
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
    def primaries(self):
        """
        :return: Primary variables
        :rtype: List[Input or Output]
        """
        return [v for v in self.bindings if isinstance(v, (Input, Output)) and v.as_primary]

    @lazy_property
    def default(self):
        """
        :return: The default value for the Lambda
        :rtype: Dict[str, Any]
        """
        return {v.name: v.default for v in self.primaries}

    @lazy_property
    def is_functional(self):
        """
        Whether the Lambda has any output variables
        :rtype: bool
        """
        return any(self.outputs)

    @lazy_property
    def oid_var(self):
        """
        :return: the oid variable
        :rtype: Variable or None
        """
        for v in self.inputs:
            if v.as_oid:
                return v
        return None

    @lazy_property
    def time_var(self):
        """
        :return: the time variable
        :rtype: Variable or None
        """
        for v in self.inputs:
            if v.as_time:
                return v
        return None

    @property
    def signature(self):
        return f"{self.module}.{self.name}${self.version}"


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




