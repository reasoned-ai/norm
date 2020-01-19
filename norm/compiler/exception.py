from antlr4.error.ErrorListener import ErrorListener

import logging
import traceback
logger = logging.getLogger('norm.compiler')


class ParseError(ValueError):
    pass


class NormErrorListener(ErrorListener):

    def __init__(self):
        super(NormErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        err_msg = "line " + str(line) + ":" + str(column) + " " + msg
        raise ParseError(err_msg)


def error_on(cond, msg):
    """
    Raise error if condition satisfied
    :param cond: the logical condition
    :type cond: object
    :param msg: the message to log
    :type msg: str
    :raise: ParseError
    """
    if cond:
        logger.error(msg)
        logger.debug(traceback.print_exc())
        raise ParseError(msg)


def same(array, another=None):
    """
    Whether every element is the same or not if one array is provided.
    If two arrays are provided, compare each element.
    :param array: the array of element
    :type array: list
    :type another: list or None
    :rtype: bool
    """
    if another is None:
        if not isinstance(array, list) or len(array) <= 1:
            return True
        e = array[0]
        return all(a == e for a in array)
    else:
        if not isinstance(another, list) or not isinstance(array, list) or len(array) != len(another):
            return False
        return all(a1 == a2 for a1, a2 in zip(array, another))
