"""Unit tests for Slice"""
import os

from norm.config import DATA_STORAGE_ROOT
from norm.models import Level, Status
from tests.utils import NormTestCase


class SliceTestCase(NormTestCase):

    def test_slice_single(self):
        self.execute("test(a: String, b: Integer);")
        test = self.execute("test;")
        self.assertTrue(test is not None)
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        lam = self.execute("test()[1];")
        self.assertTrue(lam is not test)
        self.assertTrue(lam.variables == test.variables)
        self.assertTrue(all(lam.data['a'] == ['here']))
        self.assertTrue(all(lam.data['b'] == [2]))

    def test_slice_single1(self):
        self.execute("test(a: String, b: Integer);")
        test = self.execute("test;")
        self.assertTrue(test is not None)
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        lam = self.execute("test[1];")
        self.assertTrue(lam is not test)
        self.assertTrue(lam.variables == test.variables)
        self.assertTrue(all(lam.data['a'] == ['here']))
        self.assertTrue(all(lam.data['b'] == [2]))

    def test_slice_bracket(self):
        self.execute("test(a: String, b: Integer);")
        test = self.execute("test;")
        self.assertTrue(test is not None)
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        lam = self.execute("test()[1:3];")
        self.assertTrue(lam is not test)
        self.assertTrue(lam.variables == test.variables)
        self.assertTrue(all(lam.data['a'] == ['here', 'there']))
        self.assertTrue(all(lam.data['b'] == [2, 3]))
