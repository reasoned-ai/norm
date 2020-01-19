class NormError(RuntimeError):
    pass


class Results(object):
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

    def __init__(self, context):
        """
        :param context: Compiler provides context for execution, e.g., existing bindings
        :type context: norm.compiler.Compiler
        """
        self.stack = []
        self.context = context

    def push(self, exe):
        """
        :type exe: norm.executable.NormExecutable
        """
        self.stack.append(exe)

    def pop(self):
        self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def compute(self):
        """
        Execute the command with given context
        :return: the results
        :rtype: Results
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
    Join two or more executables together.
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
    pass


class Unique(NormExecutable):
    """
    Unique values
    """
    pass


class Project(NormExecutable):
    """
    Rename or assign variables
    """
    pass


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


class Import(NormExecutable):
    """
    Import a type from a different module
    """
    pass


class Export(NormExecutable):
    """
    Export the type to a different module
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
