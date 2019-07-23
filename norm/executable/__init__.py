class NormError(RuntimeError):
    pass


class NormExecutable(object):

    VARIABLE_SEPARATOR = '__dot__'

    def __init__(self):
        from norm.models.norm import Lambda
        self.lam: Lambda = None

    def try_retrieve_type(self, session, namespaces, name, version=None, status=None):
        current_session_id = session.hash_key
        from norm.config import cache
        from norm.models.norm import retrieve_type, Lambda
        if isinstance(namespaces, str):
            key = namespaces
        else:
            key = ''.join(sorted(namespaces))
        key = (key, name, version, status)
        lam = cache.get(key)
        if lam is not None:
            if lam._sa_instance_state.session_id != current_session_id:
                new_lam: Lambda = session.merge(lam)
                # TODO: might have other states need to be kept
                new_lam._data = lam._data
                lam = new_lam
            return lam
        lam = retrieve_type(namespaces, name, version, status)
        cache[key] = lam
        return lam

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

    def __init__(self, variables):
        """
        The projection definition
        :param variables: a list of variables to project on
        :type variables: List[norm.executable.variable.VariableName]
        """
        super().__init__()
        self.variables = variables

    @property
    def with_unquote(self):
        from norm.executable.schema.variable import UnquoteVariable
        return any(isinstance(v, UnquoteVariable) for v in self.variables)

    @property
    def num(self):
        return len(self.variables)



