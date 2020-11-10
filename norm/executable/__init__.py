from typing import List, TYPE_CHECKING, Optional, cast

from norm import random_name
from norm.parser import TEMP_VAR_STUB, SEPARATOR
from norm.config import USE_DASK, DataFrame

if TYPE_CHECKING:
    from norm.compiler import NormCompiler
    from norm.models.norm import Lambda, Variable

import logging
logger = logging.getLogger("norm.executable")


class EngineError(RuntimeError):
    pass


class NormExecutable(object):
    """
    The execution plan
    """

    def __init__(self, context: "NormCompiler", dependents: List["NormExecutable"] = None, type_: "Lambda" = None):
        """
        :param context: Compiler provides context for execution, e.g., existing bindings
        :param dependents: dependent executables
        :param type_: the Lambda for the execution results, not necessarily for every execution
        """
        self.stack: List["NormExecutable"] = dependents or []
        self._lam: "Lambda" = type_ or None
        self.context: "NormCompiler" = context

    @property
    def lam(self) -> Optional["Lambda"]:
        """
        Get the Lambda for the results
        """
        return self._lam

    @lam.setter
    def lam(self, o: "Lambda"):
        """
        Set the Lambda for the results
        """
        self._lam = o

    def prepare(self) -> DataFrame:
        """
        Prepare context before executing
        :return: the prepared data
        """
        if len(self.stack) == 0:
            return self._lam.empty_data
        else:
            # execute stacks
            for e in self.stack:
                v = e.execute()
            # TODO: return merged data
            return self._lam.empty_data

    def project(self, data: DataFrame) -> Optional["Variable"]:
        """
        Project computed data to context
        :return: projected variable
        """
        var = self.lam.random_var()
        var.data = data
        # TODO: project back to the context
        return var

    def execute(self) -> Optional["Variable"]:
        """
        Execute the command with given context
        :return: the results
        """
        raise NotImplementedError


class Statements(NormExecutable):
    """
    Execute a list of statements and return the last results
    """

    def execute(self) -> Optional["Variable"]:
        results = None
        for exe in self.stack:
            if exe is not None:
                results = exe.execute()
        return results


class Argument(NormExecutable):

    def __init__(self, context: "NormCompiler", expr: "NormExecutable" = None,
                 variable_name: str = None, is_query: bool = False):
        """
        :param context: Compiler provides context for execution, e.g., existing bindings
        :param expr: dependent expression
        :param variable_name: the variable name for the argument
        """
        super(Argument, self).__init__(context, [expr], None)
        self.variable_name = variable_name
        self.is_query = is_query

    def execute(self) -> Optional["Variable"]:
        return self.stack[0].execute()


def _new_col(scope: str, col: str) -> str:
    if col == '_oid':
        return scope
    else:
        return SEPARATOR.join([scope, col])


class AtomicEvaluation(NormExecutable):
    """
    Query or construction on the atomic lambda is an evaluation
    """

    def prepare(self) -> DataFrame:
        """
        Prepare context before executing
        :return: the prepared data
        """
        if len(self.stack) == 0:
            return self._lam.empty_data
        else:
            # get arguments
            e: Argument
            da: List[DataFrame] = []
            for i, e in enumerate(self.stack):
                v = e.execute()
                if e.variable_name is not None:
                    inp = self._lam.get(e.variable_name)
                    assert(inp is not None)
                else:
                    inp = self._lam.inputs[i]
                if v is None or v.type_.id != inp.type_.id:
                    # TODO: projection
                    raise NotImplementedError
                else:
                    data = v.data.rename(columns={col: _new_col(inp.name, col) for col in v.data.columns})
                    da.append(data)
            if len(da) > 1:
                # TODO: merge data
                raise NotImplementedError
            else:
                return da[0]

    def execute(self) -> Optional["Variable"]:
        var = self.lam.random_var()
        data = self.prepare()
        data = self.lam.func(data)
        var.data = data
        return var


class Query(NormExecutable):
    """
    Query a non-atomic Lambda
    """
    def execute(self) -> Optional["Variable"]:
        var = self.random_var()
        # TODO: get args dependents
        args = [arg.execute().value for arg in self.stack]
        var.value = self.lam.func(*args)
        return var


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
    def __init__(self, context, dependents=None, variable=None, type_=None):
        """
        :param variable: the name of the variable to pivot on
        :type variable: str
        """
        super().__init__(context, dependents=dependents, type_=type_)
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
    def __init__(self, context, dependents=None, variables=None, type_=None):
        """
        :type variables: List[str]
        """
        super().__init__(context, dependents=dependents, type_=type_)
        self.variables: List[str] = variables


class Construction(NormExecutable):
    """
    Construct objects and fill values
    """

    def execute(self) -> Optional["Variable"]:
        var = self.random_var()
        args = [arg.execute().value for arg in self.stack]
        # TODO: construct values
        return var


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


class TypeDefinition(NormExecutable):
    """
    Define a Lambda
    """

    def execute(self) -> Optional["Variable"]:
        var = self.stack[0].execute()
        self.lam._data = var.data
        return var


class CodeExecution(NormExecutable):
    """
    Execute code in Python or SQL
    """
    def __init__(self, context, dependents=None, type_=None, code=''):
        super().__init__(context, dependents=dependents, type_=type_)
        self.lam.define(code)


