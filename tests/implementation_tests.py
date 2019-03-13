"""Unit tests for Implementation"""
from norm.models import Lambda, retrieve_type
from norm.utils import hash_df
from tests.utils import NormTestCase
from pandas import DataFrame


class ImplementationTestCase(NormTestCase):

    def test_add_data(self):
        self.execute("test(a: Integer, b: String);")
        lam = self.execute("test := (1, 'sf')"
                           "     |  (2, 'sfs')"
                           "     |  (4, 'fs')"
                           "     ;")
        self.assertTrue(lam is not None)
        df = DataFrame(data={'a': [1, 2, 4],
                             'b': ['sf', 'sfs', 'fs']},
                       columns=['a', 'b'])[['a', 'b']]
        self.assertTrue(len(lam.revisions) == 1)
        self.assertTrue(lam.revisions[0].query == hash_df(df))

    def test_add_data_and_declare(self):
        lam = self.execute("test := (1, 'sf')"
                           "     |  (2, 'sfs')"
                           "     |  (4, 'fs')"
                           "     ;")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(lam.variables[0].name == '{}0'.format(Lambda.VAR_ANONYMOUS_STUB))
        self.assertTrue(lam.variables[1].name == '{}1'.format(Lambda.VAR_ANONYMOUS_STUB))
        self.assertTrue(lam.variables[0].type_ == retrieve_type('norm.native', 'Integer'))
        self.assertTrue(lam.variables[1].type_ == retrieve_type('norm.native', 'Any'))

    def test_reset_data(self):
        self.execute("test(a: Integer, b: String);")
        lam = self.execute("test := (1, 'sf')"
                           "     |  (4, 'fs')"
                           "     ;")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 1)
        lam = self.execute("test := (1, 'sf')"
                           "     |  (2, 'sfs')"
                           "     |  (4, 'fs')"
                           "     ;")
        df = DataFrame(data={'a': [1, 2, 4],
                             'b': ['sf', 'sfs', 'fs']},
                       columns=['a', 'b'])[['a', 'b']]
        self.assertTrue(len(lam.revisions) == 1)
        self.assertTrue(lam.revisions[0].query == hash_df(df))

    def test_appending_data(self):
        self.execute("test(a: Integer, b: String);")
        lam = self.execute("test := (1, 'sf')"
                           "     |  (4, 'fs')"
                           "     ;")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 1)
        lam = self.execute("test |= (1, 'sf')"
                           "     |  (2, 'sfs')"
                           "     |  (4, 'fs')"
                           "     ;")
        self.assertTrue(len(lam.revisions) == 2)
        df = DataFrame(data={'a': [1, 2, 4],
                             'b': ['sf', 'sfs', 'fs']},
                       columns=['a', 'b'])[['a', 'b']]
        self.assertTrue(lam.revisions[1].query == hash_df(df))
        self.assertTrue(len(lam.data) == 5)
        self.assertTrue(all(lam.data['a'] == [1, 4, 1, 2, 4]))

