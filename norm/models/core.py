"""A collection of ORM sqlalchemy models for CoreLambda"""
import logging

from pandas import Series

from norm.models import norma, Register
from norm.models.norm import Lambda, Module, Variable
from norm.models.variable import Input, Output

from norm.config import DataFrame

from typing import List, Optional

logger = logging.getLogger(__name__)

__version__ = '1'


@Register()
class CoreModule(Module):
    __table_args__ = None
    __mapper_args__ = {
        'polymorphic_identity': 'module_core'
    }

    def __init__(self):
        super().__init__(name='core', description='Norm core namespace')


class CoreLambda(Lambda):
    """
    Core functions are at the computable level and predefined in the code base
    """
    __table_args__ = None

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core'
    }

    def __init__(self, name: str, description: str, version: str = None, bindings: List[Variable] = None):
        super().__init__(module=norma['core'],
                         name=name,
                         description=description,
                         version=version or __version__,
                         atomic=True,
                         bindings=bindings or [])


@Register()
class SummaryLambda(CoreLambda):
    """
    Summary of the data
    """
    __table_args__ = None

    __mapper_args__ = {
        'polymorphic_identity': 'core_summary'
    }

    def __init__(self):
        super().__init__(name='summary',
                         description='Summary of the variable of a given type',
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
class ReadLambda(CoreLambda):
    """
    Read data
    """
    __table_args__ = None

    __mapper_args__ = {
        'polymorphic_identity': 'core_read'
    }

    FORMAT_PARQUET = 'parquet'
    FORMAT_CSV = 'CSV'
    FORMAT_TSV = 'tsv'
    FORMAT_EXCEL = 'excel'

    def __init__(self):
        super().__init__(name='read',
                         description='Read data file',
                         bindings=[Input(type_=norma['native.String'], name='file_name'),
                                   Input(type_=norma['native.String'], name='format'),
                                   Output(type_=norma['native.Type'])])

    def func(self, data: DataFrame) -> DataFrame:
        if len(data) == 1:
            data = data.compute()
            file_name: str = data.iloc[0]['file_name']
            fmt: str = data.iloc[0]['format'] if 'format' in data.columns else None
            if fmt is None:
                fmt = self.FORMAT_PARQUET
            from norm.config import pdd
            if fmt == self.FORMAT_PARQUET:
                return pdd.read_parquet(file_name)
            elif fmt == self.FORMAT_CSV:
                return pdd.read_csv(file_name)
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError


@Register()
class DescribeLambda(CoreLambda):
    """
    Describe a given lambda
    """
    __table_args__ = None

    __mapper_args__ = {
        'polymorphic_identity': 'core_describe'
    }

    def __init__(self):
        super().__init__(name='describe',
                         description='Describe a given type',
                         bindings=[Input(type_=norma['native.Type'], name='type'),
                                   Output(type_=norma['core.summary'], name='summary')])

    @staticmethod
    def describe_type(signature: str) -> Optional[DataFrame]:
        lam: Lambda = norma[signature]
        if lam is None or lam.atomic:
            return None

        data = lam.data
        d = data.describe().transpose()
        numerics = set(d.index)
        non_numerics = set(data.columns).difference(numerics)
        datetimes = [col for col in non_numerics if data[col].dtype.name.find('datetime') >= 0]
        non_numerics = non_numerics.difference(datetimes)
        for col in numerics:
            d.loc[col, 'unique'] = data[col].drop_duplicates().count()
        for col in non_numerics:
            d.loc[col] = [data[col].count(), None, None, None, None, None, None, None,
                          data[col].drop_duplicates().count()]
        for col in datetimes:
            d.loc[col] = [data[col].count(), None, None, data[col].min(), None, None, None,
                          data[col].max(), data[col].drop_duplicates().count()]
        for col in data.columns:
            d.loc[col, 'type'] = lam.get(col).type_.signature or 'Any'
        d['count'] = d['count'].astype('int')
        d['unique'] = d['unique'].astype('int')
        return d

    def func(self, data: DataFrame) -> DataFrame:
        return data['type'].apply(lambda x: self.describe_type(x['type'].values[0])).reset_index()


@Register()
class RenameLambda(CoreLambda):
    """
    Rename variables for a given lambda
    """
    __table_args__ = None

    __mapper_args__ = {
        'polymorphic_identity': 'core_rename'
    }

    def __init__(self):
        super().__init__(name='rename',
                         description='Rename variables for a given lambda',
                         bindings=[Input(type_=norma['native.Type'], name='type'),
                                   Input(type_=norma['native.String'], name='old'),
                                   Input(type_=norma['native.String'], name='new')])

    @staticmethod
    def rename(x: Series) -> int:
        signature: str = x['type']
        old_var: str = x['old']
        new_var: str = x['new']
        lam: Lambda = norma[signature]
        if lam is None:
            msg = f'{signature} does not exist'
            logger.error(msg)
            return 0
        lam.rename(old_var, new_var)
        lam.data.rename(columns={old_var: new_var}, inplace=True)
        return 1

    def func(self, data: DataFrame) -> DataFrame:
        data[f'{self.name}'] = data.apply(self.rename)
        return data


@Register()
class RetypeLambda(CoreLambda):
    """
    Retype variables for a given lambda
    """
    __table_args__ = None

    __mapper_args__ = {
        'polymorphic_identity': 'core_retype'
    }

    def __init__(self):
        super().__init__(name='retype',
                         description='Retype variables for a given lambda',
                         bindings=[Input(type_=norma['native.Type'], name='type'),
                                   Input(type_=norma['native.String'], name='var_name'),
                                   Input(type_=norma['native.Type'], name='var_type')])

    @staticmethod
    def retype(x: Series) -> int:
        signature: str = x['type']
        var_name: str = x['var_name']
        var_type: str = x['var_type']
        lam: Lambda = norma[signature]
        if lam is None:
            msg = f'{signature} does not exist'
            logger.error(msg)
            return 0
        type_ = norma[var_type]
        if type_ is None:
            msg = f'{var_type} does not exist'
            logger.error(msg)
            return 0
        lam.retype(var_name, type_)
        lam.data[var_name].astytpe(type_.dtype, inplace=True)
        return 1

    def func(self,  data: DataFrame) -> DataFrame:
        data[f'{self.name}'] = data.apply(self.retype)
        return data

