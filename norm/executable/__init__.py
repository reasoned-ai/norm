from norm.literals import ConstantType


class NormError(RuntimeError):
    pass


class NormExecutable(object):

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
        :return: the Lambda to be returned
        :rtype: norm.models.norm.Lambda
        """
        return None


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

    def num(self):
        return len(self.variables)


class Constant(NormExecutable):

    def __init__(self, type_, value):
        """
        The constant
        :param type_: the name of the constant type, e.g.,
                      [none, bool, integer, float, string, unicode, pattern, uuid, url, datetime]
        :type type_: ConstantType
        :param value: the value of the constant
        :type value: Union[str, unicode, int, float, bool, datetime.datetime, NoneType]
        """
        super().__init__()
        self.type_ = type_  # type: ConstantType
        self.value = value

    def __str__(self):
        if self.type_ in [ConstantType.STR, ConstantType.PTN, ConstantType.UID, ConstantType.URL]:
            return '"{}"'.format(self.value)
        elif self.type_ in [ConstantType.FLT, ConstantType.INT, ConstantType.BOOL]:
            return '{}'.format(self.value)
        elif self.type_ == ConstantType.DTM:
            return self.value.strftime('"%Y-%m-%d %H:%M:%S"')
        else:
            raise NotImplementedError

    def execute(self, context):
        return self.value


class ListConstant(Constant):

    def __init__(self, type_, value):
        """
        A list of constant of the same constant type
        :param type_: the name of the constant type
        :type type_: ConstantType
        :param value: the value of the constant
        :type value: List
        """
        assert(isinstance(value, list))
        super().__init__(type_, value)

    def __str__(self):
        return '[' + ','.join(str(v) for v in self.value) + ']'

    def execute(self, context):
        return self.value


