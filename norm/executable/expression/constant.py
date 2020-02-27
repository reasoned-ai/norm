from norm.grammar.literals import ConstantType
import datetime
from typing import Union, List


class Constant(object):

    def __init__(self, type_, value=None):
        """
        The constant
        :param type_: the name of the constant type, e.g.,
                      [none, bool, integer, float, string, unicode, pattern, uuid, url, datetime]
        :type type_: ConstantType
        :param value: the value of the constant
        :type value: Union[str, int, float, bool, datetime.datetime, None]
        """
        self.type_: ConstantType = type_
        self.value: Union[str, int, float, bool, datetime.datetime] = value

    def __str__(self):
        if self.type_ in [ConstantType.STR, ConstantType.PTN, ConstantType.UID, ConstantType.URL]:
            return '"{}"'.format(self.value)
        elif self.type_ in [ConstantType.FLT, ConstantType.INT, ConstantType.BOOL]:
            return '{}'.format(self.value)
        elif self.type_ == ConstantType.DTM:
            return self.value.strftime('"%Y-%m-%d %H:%M:%S"')
        else:
            return '{}'.format(self.value)

    def __repr__(self):
        return str(self)

    def execute(self, context):
        return self.value


class TupleConstant(Constant):

    def __init__(self, types, values):
        """
        A tuple of constants
        :param types: the list of the types
        :type types: Tuple
        :param values: the list of the values
        :type values: Tuple
        """
        assert(isinstance(values, tuple))
        assert(isinstance(types, tuple))
        super().__init__(types, values)

    def __str__(self):
        return '{}'.format(self.value)


class ListConstant(Constant):

    def __init__(self, type_, values):
        """
        A list of constant of the same constant type
        :param type_: the name of the constant type
        :type type_: ConstantType
        :param values: the value of the constant
        :type values: List[Union[str, int, float, bool, datetime.datetime]]
        """
        assert(isinstance(values, list))
        super().__init__(type_, values)

