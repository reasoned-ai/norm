from norm.executable import NormExecutable
from norm.executable import Projection
from pandas import DataFrame


class NormExpression(NormExecutable):

    def __init__(self):
        super().__init__()
        self.projection: Projection = None
        self.data: DataFrame = None
        self.description: str = None

