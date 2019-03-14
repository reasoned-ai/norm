from norm.grammar.literals import COP

from norm.executable import Projection
from norm.executable.expression import NormExpression

import logging
logger = logging.getLogger(__name__)


class ArgumentExpr(NormExpression):

    def __init__(self, variable=None, op=None, expr=None, projection=None):
        """
        The argument expression project to a new variable, either assigning or conditional.
        :param variable: the variable
        :type variable: norm.executable.variable.VariableName or None
        :param expr: the arithmetic expression for the variable
        :type expr: Union[norm.executable.expression.arithmetic.ArithmeticExpr,
                          norm.executable.expression.slice.SliceExpr,
                          norm.executable.expression.evaluation.EvaluationExpr,
                          norm.executable.variable.VariableName] or None
        :param op: the conditional operation
        :type op: COP or None
        :param projection: the projection
        :type projection: Projection or None
        """
        super().__init__()
        self.variable = variable
        self.expr = expr
        self.op = op
        self.projection = projection

    def serialize(self):
        pass


