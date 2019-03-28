from norm.executable import NormExecutable


class NormSchema(NormExecutable):

    def __init__(self):
        from norm.models.norm import Lambda
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
        :rtype: norm.models.norm.Lambda
        """
        return self.lam
