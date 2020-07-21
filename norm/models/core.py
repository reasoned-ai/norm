"""A collection of ORM sqlalchemy models for CoreLambda"""
import logging

from norm.models import norma, Registrable, Register
from norm.models.norm import Lambda, Module, Variable
from norm.models.variable import Input, Output
from typing import List

logger = logging.getLogger(__name__)

__version__ = '1'


@Register()
class CoreModule(Module):
    __mapper_args__ = {
        'polymorphic_identity': 'module_core'
    }

    def __init__(self):
        super().__init__(name='core', description='Norm core namespace')


class CoreLambda(Lambda, Registrable):
    """
    Core functions are at the computable level and predefined in the code base
    """
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core'
    }

    def __init__(self, name: str, description: str, module: Module = None, version: str = None,
                 atomic: bool = True, bindings: List[Variable] = None):
        super().__init__(module=module or norma['core'],
                         name=name,
                         description=description,
                         version=version or __version__,
                         atomic=atomic,
                         bindings=bindings or [])

    def exists(self):
        return [CoreLambda.name == self.name,
                CoreLambda.version == self.version]

    def empty_data(self):
        return None


@Register()
class SummaryLambda(CoreLambda):
    """
    Summary of the data
    """
    __mapper_args__ = {
        'polymorphic_identity': 'core_summary'
    }

    def __init__(self):
        super().__init__(name='summary',
                         description='Summary of the data of a given type',
                         bindings=[Input(type_=norma['native.String'], name='name'),
                                   Input(type_=norma['native.Type'], name='type'),
                                   Input(type_=norma['native.Integer'], name='count'),
                                   Input(type_=norma['native.Integer'], name='unique'),
                                   Input(type_=norma['native.Any'], name='min'),
                                   Input(type_=norma['native.Any'], name='max'),
                                   Input(type_=norma['native.Any'], name='mean'),
                                   Input(type_=norma['native.Any'], name='median'),
                                   Input(type_=norma['native.Any'], name='std')])


@Register()
class DescribeLambda(CoreLambda):
    """
    Describe a given lambda
    """
    __mapper_args__ = {
        'polymorphic_identity': 'core_describe'
    }

    def __init__(self):
        super().__init__(name='describe',
                         description='Describe a given type',
                         bindings=[Input(type_=norma['native.Type'], name='type'),
                                   Output(type_=norma['core.summary'], name='summary')])

    def func(self):
        # TODO revisit
        inp: Input = self.inputs[0]
        d = inp.data.describe().transpose()
        numerics = set(d.index)
        non_numerics = set(inp.data.columns).difference(numerics)
        datetimes = [col for col in non_numerics if inp.data[col].dtype.name.find('datetime') >= 0]
        non_numerics = non_numerics.difference(datetimes)
        for col in numerics:
            d.loc[col, 'unique'] = inp.data[col].drop_duplicates().count()
        for col in non_numerics:
            d.loc[col] = [inp.data[col].count(), None, None, None, None, None, None, None,
                          inp.data[col].drop_duplicates().count()]
        for col in datetimes:
            d.loc[col] = [inp.data[col].count(), None, None, inp.data[col].min(), None, None, None,
                          inp.data[col].max(), inp.data[col].drop_duplicates().count()]
        for col in inp.data.columns:
            d.loc[col, 'type'] = inp.type_.get(col).type_.signature or 'Any'
        d['count'] = d['count'].astype('int')
        d['unique'] = d['unique'].astype('int')
        out: Output = self.outputs[0]
        out.data = d.loc[self.lam.data.columns, ['type', 'count', 'unique', 'min', 'max', 'mean', '50%', 'std']]
        out.data.index.name = 'name'
        out.data.reset_index(inplace=True)


@Register()
class RenameLambda(CoreLambda):
    """
    Rename variables for a given lambda
    """
    __mapper_args__ = {
        'polymorphic_identity': 'core_rename'
    }

    def __init__(self):
        super().__init__(name='rename',
                         description='Rename variables for a given lambda',
                         bindings=[Input(type_=norma['native.Type'], name='type'),
                                   Input(type_=norma['native.String'], name='old'),
                                   Input(type_=norma['native.String'], name='new')])

    def func(self):
        # TODO revisit
        lam: Input = self.inputs[0]
        old: Input = self.inputs[1]
        new: Input = self.inputs[2]
        lam.type_.rename(old.data, new.data)
        lam.data.rename(columns={old.data: new.data}, inplace=True)


@Register()
class RetypeLambda(CoreLambda):
    """
    Retype variables for a given lambda
    """
    __mapper_args__ = {
        'polymorphic_identity': 'core_retype'
    }

    def __init__(self):
        super().__init__(name='retype',
                         description='Retype variables for a given lambda',
                         bindings=[Input(type_=norma['native.Type'], name='type'),
                                   Input(type_=norma['native.String'], name='var_name'),
                                   Input(type_=norma['native.Type'], name='var_type')])

    def func(self):
        # TODO revisit
        lam: Input = self.inputs[0]
        name: str = self.inputs[1].scalar
        type_: Lambda = self.inputs[2].scalar
        lam.type_.retype(name, type_)
        lam.data[name].astype(type_.dtype, inplace=True)
