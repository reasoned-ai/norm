from textwrap import dedent

from pandas import DataFrame

from norm.executable import NormError
from norm.executable.expression import NormExpression
import logging
logger = logging.getLogger(__name__)


class CodeExpr(NormExpression):

    def __init__(self, code):
        """
        Evaluate a piece of code in python
        :param code: a piece of code in string
        :type code: str
        """
        super().__init__()
        self.code = code
        self.eval_code = None
        self.exec_code = None

    def __str__(self):
        return self.code

    def compile(self, context):
        self.lam = context.temp_lambda([])
        lines = [line for line in self.code.split('\n') if line.strip() != '']
        self.eval_code = dedent(lines[-1])
        self.exec_code = dedent('\n'.join(lines[:-1]))
        return self

    def execute(self, context):
        try:
            g = context.python_context
            exec(self.exec_code, g, g)
            df = eval(self.eval_code, g, g)
            assert(df, DataFrame)
            self.lam.data = df
            return df
        except Exception:
            msg = 'Execution of {} failed'.format(self.code)
            logger.error(msg)
            raise NormError(msg)
