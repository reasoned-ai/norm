"""Unit tests for Slice"""
from tests.utils import NormTestCase


class SliceTestCase(NormTestCase):

    def test_slice_single(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test()[1];")
        self.assertTrue(all(data['a'] == ['here']))
        self.assertTrue(all(data['b'] == [2]))

    def test_slice_single1(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test[1];")
        self.assertTrue(all(data['a'] == ['here']))
        self.assertTrue(all(data['b'] == [2]))

    def test_slice_bracket(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test()[1:3];")
        self.assertTrue(all(data['a'] == ['here', 'there']))
        self.assertTrue(all(data['b'] == [2, 3]))

    def test_slice_undefined_ends(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test[1:];")
        self.assertTrue(all(data['a'] == ['here', 'there']))
        self.assertTrue(all(data['b'] == [2, 3]))
        data = self.execute("test[:2];")
        self.assertTrue(all(data['a'] == ['test', 'here']))
        self.assertTrue(all(data['b'] == [1, 2]))

    def test_slice_negative_ends(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test[:-1];")
        self.assertTrue(all(data['a'] == ['test', 'here']))
        self.assertTrue(all(data['b'] == [1, 2]))

