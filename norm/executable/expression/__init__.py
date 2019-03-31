import enum

from norm.executable import NormExecutable
from norm.executable import Projection
from pandas import DataFrame, Series, concat


class Strategy(enum.Enum):
    """
    Strategy to unify inputs:
        shortest: align the data and cut to the shortest length. If two inputs, one with a list of 10 objects, the
                  other with a list of 2 objects. The unified data contains 2 objects.
        longest: align the data to the longest length. Fill with n/a or type defaults.
    """
    SHORTEST = 'shortest'
    LONGEST = 'longest'


class NormExpression(NormExecutable):

    def __init__(self):
        super().__init__()
        self.projection: Projection = None
        self.data: DataFrame = None
        self.description: str = None

    def unify(self, inputs, strategy=Strategy.LONGEST):
        """
        Unify multi-variates into one DataFrame.
        :param inputs: the dictionary of the input values
        :type inputs: Dict
        :param strategy: the strategy to align inputs
        :type strategy: Strategy
        :return: the unified DataFrame
        :rtype: DataFrame
        """
        from norm.models.norm import Lambda
        lambda_inputs = {}
        list_inputs = {}
        dataframe_inputs = {}
        constant_inputs = {}
        for k, v in inputs.items():
            if isinstance(v, Lambda):
                lambda_inputs[k] = v
            elif isinstance(v, (list, Series)):
                list_inputs[k] = v
            elif isinstance(v, DataFrame):
                dataframe_inputs[k] = v
            else:
                constant_inputs[k] = v
        to_concat = [DataFrame(list_inputs)]
        for k, v in dataframe_inputs.items():
            if len(v.columns) == 1:
                renames = {col: k for col in v.columns}
            else:
                renames = {col: '{}.{}'.format(k, col) for col in v.columns}
            to_concat.append(v.rename(columns=renames))
        rt = concat(to_concat, axis=1)
        if len(rt) == 0:
            for k, v in constant_inputs.items():
                rt.loc[0, k] = v
        else:
            for k, v in constant_inputs.items():
                rt[k] = v
        return rt
