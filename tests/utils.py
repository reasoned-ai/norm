import unittest

import hashids

import norm

hashid = hashids.Hashids()

__all__ = ['NormTestCase']


class NormTestCase(unittest.TestCase):

    def setUp(self):
        norm.configure(db_path='norm/db/norm.db',
                       data_path='data')
        self.module_name = norm.random_name()

    def execute(self, script):
        from norm.engine import execute
        return execute(script, self.module_name, globals())

    def assertNoDuplicates(self, result, var_name):
        """
        All values in the column are distinct
        :param result: the result to check
        :type result: pandas.DataFrame
        :param var_name: the column name
        :type var_name: str
        :rtype: bool
        """
        self.assertTrue(len(result[var_name].drop_duplicates()) == len(result.positives))
