from pandas import DataFrame
from uuid import uuid1
from hashids import Hashids
from zlib import adler32
VERSION_MIN_LENGTH = 10
h = Hashids(min_length=VERSION_MIN_LENGTH)


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
    :return: int64
    """
    return uuid1().int >> 64


def new_version():
    """
    Create a random version
    :return:
    """
    return h.encode(uuid_int())


def random_name():
    """
    Create a random name
    :return:
    """
    return Hashids().encode(uuid1().int >> 96)
