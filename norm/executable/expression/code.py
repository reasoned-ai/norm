from norm.executable.expression import NormExpression


class CodeExpr(NormExpression):

    def __init__(self, code):
        """
        Evaluate a piece of code in python
        :param code: a piece of code in string
        :type code: str
        """
        super().__init__()
        self.code = code

    def serialize(self):
        pass

