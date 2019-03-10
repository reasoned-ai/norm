from norm.executable import NormExecutable
from norm.executable import Projection


class NormExpression(NormExecutable):

    def __init__(self):
        super().__init__()
        self._projection = None  # type: Projection

    @property
    def projection(self):
        return self._projection

    @projection.setter
    def projection(self, value):
        """
        :param value: set the projection
        :type value: Projection
        """
        self._projection = value

    def serialize(self):
        """
        Serialize the compiled expression to a query string template and a list of query variables
        :return: Tuple[str, List[norm.models.norm.Variable]]
        """
        raise NotImplementedError


def deserialize(query, variables):
    """
    De-serialize the query string template with given variables to a NormExpression
    :param query: the query string with '{{ variable }}' as the template to refer to the Lambda
    :type query: str
    :param variables: a list of Variable (name, type) to be bound to the query
    :type variables: List[norm.models.norm.Variable]
    :return: the de-serialized expression
    :rtype: NormExpression
    """
    raise NotImplementedError
