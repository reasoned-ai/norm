from pandas import DataFrame
from hashids import Hashids
from zlib import adler32
h = Hashids()


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
