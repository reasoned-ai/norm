from norm.executable.expression import NormExpression


class CodeExpr(NormExpression):

    def __init__(self, mode, code):
        """
        Evaluate a piece of code in keras/python/sql
        :param mode: the code execution mode, {keras, python, sql, query}
        :type mode: CodeMode
        :param code: a piece of code in string
        :type code: str
        """
        super().__init__()
        self.mode = mode
        self.code = code

    def serialize(self):
        pass
