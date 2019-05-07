"""A collection of ORM sqlalchemy models for PythonLambda"""
from textwrap import dedent

from pandas import DataFrame, Series
from sqlalchemy import Column, Text, orm

from norm.executable import NormError
from norm.models.norm import Lambda, Status, Variable

import logging
logger = logging.getLogger(__name__)


class PythonLambda(Lambda):

    VAR_INPUTS = 'inputs'

    code = Column(Text, default='')

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_python'
    }

    def __init__(self, namespace, name, description, code):
        """
        Python function, inputs are wrapped into one variable, outputs are one variable too.
        :param namespace: the namespace
        :type namespace: str
        :param name: the name of the function
        :type name: str
        :param description: description
        :type description: str
        :param code: the code of the Python implementation
        :type code: str
        """
        from norm.models import lambdas
        super().__init__(namespace=namespace,
                         name=name,
                         description=description,
                         variables=[Variable(self.VAR_INPUTS, lambdas.Any),
                                    Variable(self.VAR_OUTPUT, lambdas.Any)])
        self.status = Status.READY
        self.code = dedent(code)
        self._load_func()
        self.atomic = True

    def _load_func(self):
        try:
            d = {}
            exec(self.code, d)
            self._func = d.get(self.name)
        except Exception:
            msg = 'Execution errors: \n{}'.format(self.code)
            logger.error(msg)
            raise NormError(msg)
        if self._func is None or not callable(self._func):
            msg = 'Function {} does not exist or failed to parse'.format(self.name)
            logger.error(msg)
            raise NormError(msg)

    @orm.reconstructor
    def init_on_load(self):
        self._load_func()

    def __call__(self, **inputs):
        inp: DataFrame = inputs.get(self.VAR_INPUTS)
        try:
            if inp is not None:
                df = self._func(inp)
                if isinstance(df, Series):
                    df.name = self.VAR_OUTPUT
                if isinstance(inp, DataFrame) and not isinstance(df, DataFrame):
                    raise NormError
            else:
                df = self._func()
        except Exception:
            df = DataFrame(inp.apply(self._func, axis=1), columns=[self.VAR_OUTPUT])
        return df

