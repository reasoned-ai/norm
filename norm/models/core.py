"""A collection of ORM sqlalchemy models for CoreLambda"""
import logging

from norm.models import store, Registrable, Register
from norm.models.norm import Lambda, Module
from norm.models.variable import Input, Output

logger = logging.getLogger(__name__)

__version__ = '1'


@Register()
class CoreModule(Module):
    __mapper_args__ = {
        'polymorphic_identity': 'module_core'
    }

    def __init__(self):
        super().__init__('norm.core', description='Norm core namespace')


class CoreLambda(Lambda, Registrable):
    """
    Core functions are at the computable level and predefined in the code base
    """
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core'
    }

    def __init__(self, name, description, module=None, version=None, atomic=True, bindings=None):
        super().__init__(module=module or store.core.latest,
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
        super().__init__(name='Summary',
                         description='Summary of the data of a given type',
                         bindings=[Input(type_=store.native.String.latest, name='name'),
                                   Input(type_=store.native.Type.latest, name='type'),
                                   Input(type_=store.native.Integer.latest, name='count'),
                                   Input(type_=store.native.Integer.latest, name='unique'),
                                   Input(type_=store.native.Any.latest, name='min'),
                                   Input(type_=store.native.Any.latest, name='max'),
                                   Input(type_=store.native.Any.latest, name='mean'),
                                   Input(type_=store.native.Any.latest, name='median'),
                                   Input(type_=store.native.Any.latest, name='std')])


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
                         bindings=[Input(type_=store.native.Type.latest, name='type'),
                                   Output(type_=store.core.Summary.latest, name='summary')])

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

