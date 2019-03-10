"""A collection of ORM sqlalchemy models for CoreLambda"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pandas import DataFrame
from sqlalchemy import exists

from norm.config import db
from norm.models.norm import Lambda, Variable, Status, retrieve_type

import logging
import traceback
logger = logging.getLogger(__name__)


class RegisterCores(object):
    types = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, cls):
        self.types.append((cls, self.args, self.kwargs))
        return cls

    @classmethod
    def register(cls):
        for clz, args, kwargs in cls.types:
            instance = clz(*args, **kwargs)
            in_store = db.session.query(exists().where(clz.name == instance.name)).scalar()
            if not in_store:
                logger.info('Registering class {}'.format(instance.name))
                db.session.add(instance)
        try:
            db.session.commit()
        except:
            logger.error('Type registration failed')
            logger.debug(traceback.print_exc())

    @classmethod
    def retrieve(cls, clz, *args, **kwargs):
        instance = clz(*args, **kwargs)
        stored_inst = db.session.query(clz).filter(clz.name == instance.name).scalar()
        if stored_inst is None:
            stored_inst = instance
            db.session.add(instance)
        return stored_inst


class CoreLambda(Lambda):
    """
    Core functions are at the computable level and predefined in the code base
    """
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core'
    }
    NAMESPACE = 'norm.core'

    def __init__(self, name, description, variables, dtype='object'):
        super().__init__(namespace=self.NAMESPACE,
                         name=name,
                         description=description,
                         variables=variables,
                         dtype=dtype)
        self.status = Status.READY
        self.shape = []


def native_type(name):
    return retrieve_type('norm.native', name)


@RegisterCores()
class ReadFileLambda(CoreLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core_read_file'
    }

    VAR_LAMBDA = 'lambda'
    VAR_PATH = 'path'
    VAR_PARM = 'parameters'
    VAR_EXT = 'ext'

    EXT_CSV = 'csv'
    EXT_PAR = 'parq'
    EXT_TSV = 'tsv'
    EXT_JSL = 'jsonl'

    def __init__(self):
        string_type = native_type('String')
        lambda_type = native_type('Type')
        any_type = native_type('Any')
        super().__init__(name='read',
                         description='Read data from files [.csv, .tsv, .parq, .jsonl], default to csv file'
                                     'your_lambda.read("path_to_the_file.csv", (sep="\t", skiprows=3))'
                                     'read(your_lambda, "path_to_the_file.csv", (sep="\t", skiprows=3))',
                         variables=[Variable(self.VAR_LAMBDA, lambda_type),
                                    Variable(self.VAR_PATH, string_type),
                                    Variable(self.VAR_PARM, any_type),
                                    Variable(self.VAR_EXT, string_type)])

    def query(self, inputs, outputs):
        lam = inputs.get(self.VAR_LAMBDA)
        path = inputs.get(self.VAR_PATH)
        params = inputs.get(self.VAR_PARM)
        ext = inputs.get(self.VAR_EXT)
        if lam is None or path is None:
            return None

        if isinstance(path, Lambda):
            path = path.data.iloc[0][0]
        assert(isinstance(path, str))
        if ext and isinstance(ext, Lambda):
            ext = ext.data.iloc[0][0]
        if ext is None:
            last_path = path.split('.')[-1]
            if last_path == self.EXT_CSV:
                ext = self.EXT_CSV
            elif last_path == self.EXT_PAR:
                ext = self.EXT_PAR
            elif last_path == self.EXT_TSV:
                ext = self.EXT_TSV
            elif last_path == self.EXT_JSL:
                ext = self.EXT_JSL
            else:
                ext = self.EXT_CSV
        if params is not None:
            params = params.data.to_dict()[0]

        if ext == self.EXT_CSV:
            lam.read_csv(path, params)
        elif ext == self.EXT_TSV:
            params['sep'] = '\t'
            lam.read_csv(path, params)
        elif ext == self.EXT_PAR:
            lam.read_parquet(path, params)
        elif ext == self.EXT_JSL:
            lam.read_jsonl(path)
        else:
            msg = 'Currently supported file formats: CSV (.csv), TSV (.tsv), Parquet (.parq) ' \
                  'and JSONL (.jsonl)'
            logger.error(msg)
            raise TypeError(msg)
        return lam


@RegisterCores()
class StringFormatterLambda(CoreLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core_string_formatter'
    }

    VAR_FORMATTER = 'formatter'
    VAR_VARIABLES = 'variables'

    def __init__(self):
        string_type = native_type('String')
        any_type = native_type('Any')
        formatter = Variable(self.VAR_FORMATTER, string_type)
        variables = Variable(self.VAR_VARIABLES, any_type)
        output = Variable(self.VAR_OUTPUT, string_type)
        super().__init__(name='format',
                         description='Format the strings with given inputs, the semantic is the same as Python format',
                         variables=[formatter, variables, output])

    def query(self, inputs, outputs):
        formatter = inputs.get(self.VAR_FORMATTER, None)  # type: Lambda
        variables = inputs.get(self.VAR_VARIABLES, None)  # type: Lambda
        if variables is None or formatter is None:
            return None

        v_cols = list(variables.data.columns)
        if isinstance(formatter, Lambda):
            assert(len(formatter.data) == len(variables.data))
            f_col = formatter.data.columns[0]
            df = formatter.data.reset_index().join(variables.data.reset_index())
            data = df.apply(lambda x: x[f_col].format(*[x[c] for c in v_cols]), axis=1)
        else:
            assert(isinstance(formatter, str))
            data = variables.data.apply(lambda x: formatter.format(*[x[c] for c in v_cols]), axis=1)

        lam = self.variables[-1].type_.clone()
        lam.data = DataFrame(data=data)
        return lam


@RegisterCores()
class ExtractPatternLambda(CoreLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core_extract_pattern'
    }

    VAR_PATTERN = 'pattern'
    VAR_STRING = 'string'
    VAR_FILLNA = 'fillna'

    def __init__(self):
        string_type = native_type('String')
        any_type = native_type('Any')
        super().__init__(name='extract',
                         description='Extract patterns from a string'
                                     '"(2014).*(6)".extract("2014-06") --> (2014, 6)/None'
                                     '"2014.*6".extract(s, fillna=False) --> True/False',
                         variables=[Variable(self.VAR_PATTERN, string_type),
                                    Variable(self.VAR_STRING, string_type),
                                    Variable(self.VAR_FILLNA, any_type),
                                    Variable(self.VAR_OUTPUT, any_type)])

    def query(self, inputs, outputs):
        pattern = inputs.get(self.VAR_PATTERN, None)  # type: Lambda
        string = inputs.get(self.VAR_STRING, None)  # type: Lambda
        if pattern is None or string is None:
            return None
        fill_na = inputs.get(self.VAR_FILLNA, None)  # type: Lambda
        if fill_na is not None:
            fill_na = fill_na.data

        import re

        def match(p, s):
            m = re.match(p, s)
            if m is not None:
                if len(m.groups()) == 0:
                    return True
                else:
                    return m.groups()
            else:
                return fill_na

        if isinstance(pattern.data, DataFrame):
            assert(len(pattern.data) == len(string.data))
            pdata = pattern.data.loc[:, 0]
            sdata = string.data.loc[:, 0]
            df = DataFrame({'p': pdata, 's': sdata})
            data = df.apply(lambda x: match(x.p, x.s), axis=1, result_type='expand')
        else:
            assert(isinstance(pattern.data, str))
            f = pattern.data
            data = string.data.apply(lambda x: match(f, x.s), axis=1, result_type='expand')

        lam = self.variables[-1].type_.clone()
        lam.data = DataFrame(data=data)
        return lam

