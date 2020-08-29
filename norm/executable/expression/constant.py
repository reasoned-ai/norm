from norm.config import USE_DASK
from norm.executable import NormExecutable
import datetime
from typing import Union, List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from norm.compiler import NormCompiler
    from norm.models.norm import Lambda, Variable


class Constant(NormExecutable):
    """
    Constant
    """
    def __init__(self, context: "NormCompiler", type_: "Lambda", value: object):
        super().__init__(context, dependents=[], type_=type_)
        self.var: Variable = type_.random_var()
        self.var.data = {type_.VAR_OID: [value]}

    def execute(self) -> Optional["Variable"]:
        return self.var


class MeasurementConstant(Constant):
    """
    Measurement based constant
    """
    def __init__(self, context: "NormCompiler", type_: "Lambda", value: object, unit: str):
        super(MeasurementConstant, self).__init__(context, type_, value)
        self.unit = unit


class MapToConstant(Constant):
    pass


class TupleConstant(Constant):
    pass


class ListConstant(Constant):
    pass
