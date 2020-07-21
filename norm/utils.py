from pandas import DataFrame
from uuid import uuid4
from zlib import adler32
from norm.config import hasher
import logging


def hash_df(df: DataFrame) -> str:
    """
    Create a hash string out of a DataFrame data
    :param df: the DataFrame data
    :type df: DataFrame
    :return: the hash string
    :rtype: str
    """
    if df is None:
        return ''
    # noinspection PyUnresolvedReferences
    return hasher.encode(adler32(str(df.values).encode('utf-8')))


def uuid_int32() -> int:
    """
    Create a 32bit integer from uuid
    :rtype: int
    """
    return uuid4().int & 0xffffffff


def uuid_int() -> int:
    """
    Create a 64bit integer from uuid
    :rtype: int
    """
    return uuid4().int >> 64


def new_version() -> str:
    """
    Create a random version
    :rtype: str
    """
    return hasher.encode(uuid_int())


def random_name() -> str:
    """
    Create a random name
    :rtype: str
    """
    return hasher.encode(uuid4().int)


def infodf(lg: logging.Logger, df: DataFrame):
    for line in str(df).splitlines():
        lg.info(line)


def warndf(lg: logging.Logger, df: DataFrame):
    for line in str(df).splitlines():
        lg.warning(line)


def errordf(lg: logging.Logger, df: DataFrame):
    for line in str(df).splitlines():
        lg.error(line)


def lazy_property(f):
    internal_property = '__lazy_' + f.__name__

    @property
    def lazy_property_wrapper(self):
        try:
            return getattr(self, internal_property)
        except AttributeError:
            v = f(self)
            setattr(self, internal_property, v)
            return v
        except Exception as e:
            raise e
    return lazy_property_wrapper
