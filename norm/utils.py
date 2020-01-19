from pandas import DataFrame
from uuid import uuid1
from hashids import Hashids
from zlib import adler32
from norm.config import HASH_MIN_LENGTH

h = Hashids(min_length=HASH_MIN_LENGTH)


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
    return h.encode(adler32(str(df.values).encode('utf-8')))


def uuid_int():
    """
    Create a 64 bit integer from uuid
    :rtype: int
    """
    return uuid1().int >> 64


def new_version():
    """
    Create a random version
    :rtype: str
    """
    return h.encode(uuid_int())


def random_name():
    """
    Create a random name
    :rtype: str
    """
    return Hashids().encode(uuid1().int >> 96)


def local_url(qualified_name, sep):
    """
    Create the local url for the qualified name. The local url is relative to the NORM root
    :rtype: str
    """
    return f"file://{{DATA_STORAGE_ROOT}}/{qualified_name.replace(sep, '/')}/"

