class NormError(RuntimeError):
    pass


class NormExecutable(object):

    VARIABLE_SEPARATOR = '__dot__'

    def __init__(self):
        from norm.models.norm import Lambda
        """
        The scope of the output
        """
        self.lam: Lambda = None

    def compile(self, context):
        """
        Compile the command with the given context
        :param context: the context of the executable
        :type context: norm.engine.NormCompiler
        :return: An NormExecutable
        :rtype: NormExecutable
        """
        return self

    def execute(self, context):
        """
        Execute the command with given context
        :param context: the context of the executable
        :type context: norm.engine.NormCompiler
        :return: the result
        """
        return self.lam


class Projection(NormExecutable):

    def __init__(self, variables, to_evaluate=False):
        """
        The projection definition
        :param variables: a list of variables to project on
        :type variables: List[norm.executable.variable.VariableName]
        :param to_evaluate: whether to evaluate these variables or not, default to False.
        :type to_evaluate: Boolean
        """
        super().__init__()
        self.variables = variables
        self.to_evaluate = to_evaluate

    @property
    def num(self):
        return len(self.variables)



