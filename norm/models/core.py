"""A collection of ORM sqlalchemy models for CoreLambda"""
import json

import pandas as pd
from pandas import DataFrame, Series

from norm.models import Register
from norm.models.norm import Lambda, Variable, Status

import logging
logger = logging.getLogger(__name__)


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
        self.atomic = True


@Register()
class ReadFileLambda(CoreLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core_read_file'
    }

    VAR_PATH = 'path'
    VAR_PARM = 'parameters'
    VAR_EXT = 'ext'

    EXT_CSV = 'csv'
    EXT_PAR = 'parq'
    EXT_TSV = 'tsv'
    EXT_JSL = 'jsonl'

    def __init__(self):
        from norm.models import lambdas
        super().__init__(name='read',
                         description='Read data from files [.csv, .tsv, .parq, .jsonl], default to csv file'
                                     'your_lambda.read("path_to_the_file.csv", (sep="\t", skiprows=3))'
                                     'read(your_lambda, "path_to_the_file.csv", (sep="\t", skiprows=3))',
                         variables=[Variable(self.VAR_PATH, lambdas.String),
                                    Variable(self.VAR_PARM, lambdas.Any),
                                    Variable(self.VAR_EXT, lambdas.String),
                                    Variable(self.VAR_OUTPUT, lambdas.Any)])

    def __call__(self, **inputs):
        path = inputs.get(self.VAR_PATH)
        params = inputs.get(self.VAR_PARM)
        ext = inputs.get(self.VAR_EXT)
        if path is None:
            return None

        if isinstance(path, DataFrame):
            path = path.iloc[0][0]
        assert(isinstance(path, str))
        if ext and isinstance(ext, DataFrame):
            ext = ext.iloc[0][0]
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
        if params is not None and isinstance(params, DataFrame):
            params = params.to_dict()[0]
        else:
            params = {}

        if ext == self.EXT_CSV:
            return self.read_csv(path, params)
        elif ext == self.EXT_TSV:
            params['sep'] = '\t'
            return self.read_csv(path, params)
        elif ext == self.EXT_PAR:
            return self.read_parquet(path, params)
        elif ext == self.EXT_JSL:
            return self.read_jsonl(path)
        else:
            msg = 'Currently supported file formats: CSV (.csv), TSV (.tsv), Parquet (.parq) ' \
                  'and JSONL (.jsonl)'
            logger.error(msg)
            raise TypeError(msg)

    def read_csv(self, path, params):
        return pd.read_csv(path, **params)

    def read_parquet(self, path, params):
        return pd.read_parquet(path, **params)

    def read_jsonl(self, path):
        with open(path) as f:
            return DataFrame([json.loads(line) for line in f])


@Register()
class StringFormatterLambda(CoreLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core_string_formatter'
    }

    VAR_FORMATTER = 'formatter'
    VAR_VARIABLES = 'variables'

    def __init__(self):
        from norm.models import lambdas
        formatter = Variable(self.VAR_FORMATTER, lambdas.String)
        variables = Variable(self.VAR_VARIABLES, lambdas.Any)
        output = Variable(self.VAR_OUTPUT, lambdas.String)
        super().__init__(name='format',
                         description='Format the strings with given inputs, the semantic is the same as Python format',
                         variables=[formatter, variables, output])

    def __call__(self, **inputs):
        formatter = inputs.get(self.VAR_FORMATTER, None)
        variables = inputs.get(self.VAR_VARIABLES, None)
        if variables is None or formatter is None:
            return None

        v_cols = list(variables.columns)
        if isinstance(formatter, DataFrame):
            assert(len(formatter) == len(variables))
            f_col = formatter.columns[0]
            df = formatter.reset_index().join(variables.reset_index())
            data = DataFrame(df.apply(lambda x: x[f_col].format(*[x[c] for c in v_cols]), axis=1),
                             columns=[self.VAR_OUTPUT])
        else:
            assert(isinstance(formatter, str))
            data = DataFrame(variables.apply(lambda x: formatter.format(*[x[c] for c in v_cols]), axis=1),
                             columns=[self.VAR_OUTPUT])
        return data


@Register()
class ExtractPatternLambda(CoreLambda):
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core_extract_pattern'
    }

    VAR_PATTERN = 'pattern'
    VAR_STRING = 'string'
    VAR_FILLNA = 'fillna'

    def __init__(self):
        from norm.models import lambdas
        super().__init__(name='extract',
                         description='Extract patterns from a string'
                                     '"(2014).*(6)".extract("2014-06") --> (2014, 6)/None'
                                     '"2014.*6".extract(s, fillna=False) --> True/False',
                         variables=[Variable(self.VAR_PATTERN, lambdas.String),
                                    Variable(self.VAR_STRING, lambdas.String),
                                    Variable(self.VAR_FILLNA, lambdas.Any),
                                    Variable(self.VAR_OUTPUT, lambdas.Any)])

    def __call__(self, **inputs):
        pattern = inputs.get(self.VAR_PATTERN, None)
        string = inputs.get(self.VAR_STRING, None)
        if pattern is None or string is None:
            return None
        fill_na = inputs.get(self.VAR_FILLNA, None)
        if fill_na is not None and isinstance(fill_na, Lambda):
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

        if isinstance(pattern, str):
            data = string.apply(lambda x: match(pattern, x.s), axis=1, result_type='expand')
        elif isinstance(pattern, DataFrame):
            assert(len(pattern) == len(string))
            pdata = pattern.loc[:, 0]
            sdata = string.loc[:, 0]
            df = DataFrame({'p': pdata, 's': sdata})
            data = df.apply(lambda x: match(x.p, x.s), axis=1, result_type='expand')
        elif isinstance(pattern, Series) and isinstance(string, Series):
            df = DataFrame({'p': pattern, 's': string})
            data = df.apply(lambda x: match(x.p, x.s), axis=1, result_type='expand')
        else:
            raise NotImplementedError
        return data
