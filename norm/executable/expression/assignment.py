from norm.executable.expression import NormExpression
from norm.executable.schema.variable import VariableName


class AssignmentExpr(NormExpression):

    def __init__(self, variable, expr):
        """
        Assigning the result of an expression to an object variable
        :param variable: the name of the variable
        :type variable: VariableName
        :param expr: the expression to be evaluated at
        :type expr: ArithmeticExpr
        """
        super().__init__()
        self.variable = variable
        self.expr = expr

    def serialize(self):
        pass

    def execute(self, context):
        # TODO: assign the value to the object variable
        pass
