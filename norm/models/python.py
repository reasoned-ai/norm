"""A collection of ORM sqlalchemy models for PythonLambda"""
from textwrap import dedent

from pandas import DataFrame, Series
from sqlalchemy import Column, Text, orm

from norm.executable import NormError
from norm.models.norm import Lambda, Status, Variable, retrieve_type

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
                         variables=[Variable.create(self.VAR_INPUTS, lambdas.Any)])
        self.status = Status.READY
        self.shape = []
        self.code = dedent(code)
        r = self.code.rfind('return')
        if r < 0:
            msg = 'Need to return the function in the script'
            logger.error(msg)
            raise NormError(msg)
        self.code = '{}{} ={}'.format(self.code[:r], self.name, self.code[r+6:])
        self._load_func()

    def _load_func(self):
        try:
            d = {}
            exec(self.code, d)
            self._func = d.get(self.name)
        except:
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

    def query(self, inputs, outputs):
        inp = inputs.get(self.VAR_INPUTS)  # type: Lambda
        out = Lambda()
        try:
            if inp is not None:
                out.df = self._func(inp.data)
                if isinstance(out.df, Series):
                    out.df = DataFrame(out.df)
                if isinstance(inp.data, DataFrame) and not isinstance(out.df, DataFrame):
                    raise NormError
            else:
                out.df = self._func()
        except:
            out.df = DataFrame(inp.data.apply(self._func, axis=1), columns=[self.VAR_OUTPUT])
        if isinstance(out.df, DataFrame):
            from norm.models import lambdas
            out.variables = [Variable.create(c, lambdas.Any) for c in out.df.columns]
        return out

