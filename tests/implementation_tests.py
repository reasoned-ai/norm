"""Unit tests for Implementation"""
from norm.models import norma
from norm.models.variable import Variable
from tests.utils import NormTestCase


class ImplementationTestCase(NormTestCase):

    def test_add_data(self):
        self.execute("test:: (a: Integer, b: String)")
        result = self.execute("test := (1, 'sf')"
                              "     |  (2, 'sfs')"
                              "     |  (4, 'fs')")
        self.assertTrue(result is not None)
        self.assertTrue(all(result.positives['a'] == [1, 2, 4]))

    def test_add_data_for_anonymous(self):
        result = self.execute("test := (1, 'sf')"
                              "     |  (2, 'sfs')"
                              "     |  (4, 'fs')")
        self.assertTrue(result is not None)
        var = result.lam.get(f'{Variable.VAR_ANONYMOUS_STUB}0')
        self.assertTrue(var is not None and var.type_ == norma.native.Integer.latest)
        var = result.lam.get(f'{Variable.VAR_ANONYMOUS_STUB}1')
        self.assertTrue(var is not None and var.type_ == norma.native.String.latest)

    def test_reset_data(self):
        self.execute("test:: (a: Integer, b: String)")
        result = self.execute("test := (1, 'sf')"
                              "     |  (4, 'fs')")
        self.assertTrue(result is not None)
        result2 = self.execute("test := (1, 'sf')"
                               "     |  (2, 'sfs')"
                               "     |  (4, 'fs')")
        self.assertTrue(result.type_ is not result2.type_)
        self.assertTrue(len(result.positives) == 2)
        self.assertTrue(len(result2.positives) == 3)

    def test_appending_data(self):
        self.execute("test:: (a: Integer, b: String)")
        result = self.execute("test := (1, 'sf')"
                              "     |  (4, 'fs')")
        self.assertTrue(result is not None)
        self.assertTrue(len(result.positives) == 2)
        result = self.execute("test |= (1, 'sf')"
                              "     |  (2, 'sfs')"
                              "     |  (4, 'fs')")
        self.assertTrue(len(result.positives) == 3)
        self.assertTrue(all(result.positives['a'] == [1, 4, 2]))
