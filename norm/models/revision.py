"""A collection of ORM sqlalchemy models for Revision"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from sqlalchemy import Column, Integer, String, ForeignKey, Text, orm, JSON
from sqlalchemy import Table
from sqlalchemy.orm import relationship

from norm.models.mixins import ParametrizedMixin
from norm.models.norm import Lambda, Variable
import norm.config as config

from pandas import DataFrame
import pandas as pd

import logging
logger = logging.getLogger(__name__)

Model = config.Model
metadata = Model.metadata
user_model = config.user_model


class Revision(Model, ParametrizedMixin):
    """Revision of the Lambda. All revisions for the same version are executed in memory."""
    __tablename__ = 'revisions'
    category = Column(String(128))

    PARQUET_EXT = 'parq'

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, default='')
    position = Column(Integer)
    description = Column(Text, default='')
    lambda_id = Column(Integer, ForeignKey("lambdas.id"))
    lam = relationship(Lambda, back_populates="revisions")

    __mapper_args__ = {
        'polymorphic_identity': 'revision',
        'polymorphic_on': category
    }

    def __init__(self, query, description, lam):
        self.query = query
        self.description = description
        self.lam = lam  # type: Lambda

    def save(self):
        """
        Save revision information
        """
        raise NotImplementedError

    def apply(self):
        """
        Apply revision on the Lambda
        """
        raise NotImplementedError

    def redo(self):
        """
        Re-apply revision on the Lambda
        """
        raise NotImplementedError

    def undo(self):
        """
        Revert the revision on the Lambda
        """
        raise NotImplementedError


revision_variable = Table(
    'revision_variable', metadata,
    Column('id', Integer, primary_key=True),
    Column('revision_id', Integer, ForeignKey('revisions.id')),
    Column('variable_id', Integer, ForeignKey('variables.id'))
)


class SchemaRevision(Revision):

    __mapper_args__ = {
        'polymorphic_identity': 'revision_schema'
    }

    renames = Column(JSON, default={})
    variables = relationship(Variable, secondary=revision_variable)

    def __init__(self, lam):
        super().__init__('', '', lam)

    def save(self):
        pass

    def redo(self):
        self.apply()


class AddVariableRevision(SchemaRevision):

    __mapper_args__ = {
        'polymorphic_identity': 'revision_schema_add'
    }

    def __init__(self, variables, lam):
        super().__init__(lam)
        current_variable_names = set((v.name for v in self.lam.variables))
        self.variables = [v for v in variables if v.name not in current_variable_names]

    def apply(self):
        self.lam.variables.extend(self.variables)

    def undo(self):
        for v in reversed(self.variables):
            popped_vp = self.lam.variables.pop()
            assert(v.name == popped_vp.name)


class RenameVariableRevision(SchemaRevision):

    __mapper_args__ = {
        'polymorphic_identity': 'revision_schema_rename'
    }

    def __init__(self, renames, lam):
        super().__init__(lam)
        current_variable_names = set((v.name for v in self.lam.variables))
        self.renames = dict((old_name, new_name) for old_name, new_name in renames.items()
                            if old_name in current_variable_names)

    def apply(self):
        for v in self.lam.variables:
            new_name = self.renames.get(v.name)
            if new_name is not None:
                v.name = new_name
        if self.lam and self.lam.data:
            self.lam.data.rename(columns=self.renames)

    def undo(self):
        renames_r = dict((new_name, old_name) for old_name, new_name in self.renames.items())
        for v in self.lam.variables:
            old_name = renames_r.get(v.name)
            if old_name is not None:
                v.name = old_name
        if self.lam and self.lam.data:
            self.lam.data.rename(columns=self.renames_r)


class RetypeVariableRevision(SchemaRevision):

    __mapper_args__ = {
        'polymorphic_identity': 'revision_schema_rename'
    }

    def __init__(self, variables, lam):
        super().__init__(lam)
        current_variable_names = set((v.name for v in self.lam.variables))
        self.variables = [v for v in variables if v.name in current_variable_names]
        variable_names = set((v.name for v in self.variables))
        self.num = len(variable_names)
        assert(len(self.variables) == len(variable_names))
        self.variables.extend([v for v in self.lam.variables if v.name in variable_names])

    @orm.reconstructor
    def init_on_load(self):
        self.num = int(len(self.variables) / 2)

    def apply(self):
        to_variables = self.variables[:self.num]
        retypes = dict((v.name, v.type_) for v in to_variables)
        for v in self.lam.variables:  # type: Variable
            t = retypes.get(v.name)
            if t is not None:
                v.type_ = t

    def undo(self):
        from_variables = self.variables[self.num:]
        retypes = dict((v.name, v.type_) for v in from_variables)
        for v in self.lam.variables:  # type: Variable
            t = retypes.get(v.name)
            if t is not None:
                v.type_ = t


class DeleteVariableRevision(SchemaRevision):

    __mapper_args__ = {
        'polymorphic_identity': 'revision_schema_delete'
    }

    def __init__(self, names, lam):
        super().__init__(lam)
        assert(isinstance(names, list))
        current_variable_names = set((v.name for v in self.lam.variables))
        self.renames = dict((name, '') for name in names if name in current_variable_names)
        self.variables = [v for v in self.lam.variables]

    def apply(self):
        self.lam.variables = [v for v in self.lam.variables if v.name not in self.renames]

    def undo(self):
        self.lam.variables = [v for v in self.lam.variables]


class DeltaRevision(Revision):

    __mapper_args__ = {
        'polymorphic_identity': 'revision_delta'
    }

    def __init__(self, query, description, lam):
        super().__init__(query, description, lam)
        self._delta = None

    @orm.reconstructor
    def init_on_load(self):
        self._delta = None

    @property
    def path(self):
        return '{}/{}.{}'.format(self.lam.folder, self.id, self.PARQUET_EXT)

    @property
    def delta(self):
        """
        Retrieve the delta. Load from path if not in memory.
        :return: the delta DataFrame
        :rtype: DataFrame
        """
        if self._delta is not None:
            return self._delta

        try:
            self._delta = pd.read_parquet(self.path)
        except FileNotFoundError:
            msg = 'Can not find delta from {}'.format(self.path)
            logger.error(msg)
            raise RuntimeError(msg)
        except:
            self._delta = None
        return self._delta

    @delta.setter
    def delta(self, delta):
        """
        Set the delta if it is not set yet.
        :type delta: DataFrame
        """
        if self._delta is None:
            self._delta = delta

    def save(self):
        if self.delta is None:
            return

        try:
            self._delta.to_parquet(self.path)
        except IOError:
            msg = 'IO problem: can not save delta to {}'.format(self.path)
            logger.error(msg)
            raise
        except:
            msg = 'Other problem: can not save delta to {}'.format(self.path)
            logger.error(msg)
            raise


class ConjunctionRevision(DeltaRevision):

    __mapper_args__ = {
        'polymorphic_identity': 'revision_delta_conjunction'
    }

    def __init__(self, query, description, lam):
        super().__init__(query, description, lam)

    def apply(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass


class DisjunctionRevision(DeltaRevision):

    __mapper_args__ = {
        'polymorphic_identity': 'revision_delta_disjunction'
    }

    def __init__(self, query, description, lam):
        super().__init__(query, description, lam)
        self.orig_df = None

    def apply(self):
        self.orig_df = self.lam.df
        if self.lam.df is not None:
            self.lam.df = self.lam.df.append(self.delta)
        else:
            self.lam.df = self.delta

    def undo(self):
        self.lam.df = self.orig_df

    def redo(self):
        self.apply()


class FitRevision(DeltaRevision):

    __mapper_args__ = {
        'polymorphic_identity': 'revision_delta_fit'
    }

    def __init__(self, query, description, lam):
        super().__init__(query, description, lam)

    def apply(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass
