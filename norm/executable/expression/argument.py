from norm.grammar.literals import COP
from norm.executable import Projection
from norm.executable.constant import Constant

from typing import Union
import logging
logger = logging.getLogger(__name__)


class ArgumentExpr(object):

    def __init__(self, variable=None, op=None, expr=None, projection=None):
        """
        The argument expression project to a new variable, either assigning or conditional.
        :param variable: the variable
        :type variable: VariableName
        :param expr: the arithmetic expression for the variable
        :type expr: Union[norm.executable.expression.arithmetic.ArithmeticExpr,
                          norm.executable.expression.slice.SliceExpr,
                          norm.executable.expression.evaluation.EvaluationExpr,
                          norm.executable.variable.VariableName]
        :param op: the conditional operation
        :type op: COP
        :param projection: the projection
        :type projection: Projection
        """
        super().__init__()
        from norm.executable.schema.variable import VariableName
        from norm.executable.expression.arithmetic import ArithmeticExpr
        from norm.executable.expression.slice import SliceExpr
        from norm.executable.expression.evaluation import EvaluationExpr
        self.variable: VariableName = variable
        self.expr: Union[ArithmeticExpr, SliceExpr, EvaluationExpr, VariableName] = expr
        self.op: COP = op
        self.projection: Projection = projection

    @property
    def is_constant(self):
        return isinstance(self.expr, Constant)
