from pandas import DataFrame
from uuid import uuid1
from zlib import adler32
from norm.config import hasher


def hash_df(df):
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


def uuid_int():
    """
    Create a 64bit integer from uuid
    :rtype: int
    """
    return uuid1().int >> 64


def new_version():
    """
    Create a random version
    :rtype: str
    """
    return hasher.encode(uuid_int())


def random_name():
    """
    Create a random name
    :rtype: str
    """
    return hasher.encode(uuid1().int)


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
