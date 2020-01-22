from typing import List


class NormError(RuntimeError):
    pass


class Results(object):
    @property
    def bindings(self):
        """
        Variable bindings
        :return: all variables involved in the computation
        :rtype: List[norm.models.norm.variable.Variable]
        """
        raise NotImplementedError

    @property
    def positives(self):
        """
        Positive results
        """
        raise NotImplementedError

    @property
    def negatives(self):
        """
        Negative results
        """
        raise NotImplementedError

    @property
    def unknowns(self):
        """
        Unknown results
        """
        raise NotImplementedError


class NormExecutable(object):

    def __init__(self, context, dependents=None):
        """
        :param context: Compiler provides context for execution, e.g., existing bindings
        :type context: norm.compiler.NormCompiler
        :param dependents: dependent executables
        :type dependents: List[NormExecutable]
        """
        self.stack = dependents or []
        self._lam = None
        self.context = context

    def push(self, exe):
        """
        :type exe: NormExecutable
        """
        self.stack.append(exe)

    def pop(self):
        """
        :rtype: NormExecutable
        """
        self.stack.pop()

    def peek(self):
        """
        :rtype: NormExecutable
        """
        return self.stack[-1]

    @property
    def lam(self):
        """
        Get the Lambda for the results
        :rtype: norm.models.norm.Lambda or None
        """
        raise NotImplementedError

    @lam.setter
    def lam(self, o):
        """
        Set the Lambda for the results
        :type o: norm.models.norm.Lambda
        """
        self._lam = o

    def compute(self):
        """
        Execute the command with given context
        :return: the results
        :rtype: Results or None
        """
        raise NotImplementedError


class TypeDeclaration(NormExecutable):
    """
    Declare a type
    """
    pass


class LoadData(NormExecutable):
    """
    Full scan of the data, optionally with filters
    """
    pass


class Filter(NormExecutable):
    """
    Filter data with conditions
    """
    pass


class Join(NormExecutable):
    """
    Join two or more executables together. If only one provided, it joins the current scope.
    """
    pass


class ConditionJoin(Join):
    """
    Join under conditions.
    """
    pass


class WindowJoin(ConditionJoin):
    """
    Join with windowing conditions
    """
    pass


class CrossJoin(Join):
    """
    Cross join two or more executables.
    """
    pass


class Union(NormExecutable):
    """
    Combine two or more executables together.
    """
    pass


class Difference(NormExecutable):
    """
    Negate rows from the first executable which appear in the second executable
    """
    pass


class Aggregate(NormExecutable):
    """
    Quantified executions
    """
    pass


class Pivot(NormExecutable):
    """
    Value to variable expansion
    """
    def __init__(self, context, dependents=None, variable=None):
        """
        :param variable: the name of the variable to pivot on
        :type variable: str
        """
        super().__init__(context, dependents=dependents)
        self.variable = variable


class Unique(NormExecutable):
    """
    Unique values
    """
    pass


class Project(NormExecutable):
    """
    Rename or assign variables
    """
    def __init__(self, context, dependents=None, variables=None):
        """
        :type variables: List[str]
        """
        super().__init__(context, dependents)
        self.variables: List[str] = variables


class Construction(NormExecutable):
    """
    Construct objects and fill values
    """
    pass


class Code(NormExecutable):
    """
    Load relation from other code, e.g., python or sql
    """
    pass


class Return(NormExecutable):
    """
    Assign results to return outputs
    """
    pass


class Implication(NormExecutable):
    """
    Implication blocks
    """
    pass


class Negation(NormExecutable):
    """
    Negate results
    """
    pass


class DefineType(NormExecutable):
    """
    Define a Lambda
    """
    pass
