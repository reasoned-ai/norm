import re
from typing import List

from norm.utils import random_name
from norm.parser import *


class Var(object):
    def __init__(self, name):
        """
        Variable placeholder with the name. If the name is a formatted string that depends on other variables, it is
        a pivoting variable
        :param name: the name of the variable
        :type name: str
        """
        self.name: str = name
        self.pivot: bool = name.startswith(('f', 'rf', 'rf')) and name.find('{') > 0

    @property
    def dependents(self):
        """
        :rtype: List[str]
        """
        return re.findall(r'{([^{}]*)}', self.name)


def random_output_variable():
    return Var(OUTPUT_VAR_STUB + random_name())


def random_temp_variable():
    return Var(TEMP_VAR_STUB + random_name())


