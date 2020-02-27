"""Unit tests for Slice"""
from tests.utils import NormTestCase


class SliceTestCase(NormTestCase):

    def setUp(self):
        super().setUp()
        self.execute("""
        test
        :: (a: String, b: Integer)
        := ('test', 1)
         | ('here', 2)
         | ('there', 3)
        """)

    def test_slice_single(self):
        result = self.execute("test[1]")
        self.assertTrue(all(result.positives['a'] == ['here']))
        self.assertTrue(all(result.positives['b'] == [2]))

    def test_slice_bracket(self):
        result = self.execute("test[1:3]")
        self.assertTrue(all(result.positives['a'] == ['here', 'there']))
        self.assertTrue(all(result.positives['b'] == [2, 3]))

    def test_slice_undefined_ends(self):
        result = self.execute("test[1:]")
        self.assertTrue(all(result.positives['a'] == ['here', 'there']))
        self.assertTrue(all(result.positives['b'] == [2, 3]))
        result = self.execute("test[:2]")
        self.assertTrue(all(result.positives['a'] == ['test', 'here']))
        self.assertTrue(all(result.positives['b'] == [1, 2]))

    def test_slice_negative_ends(self):
        result = self.execute("test[:-1]")
        self.assertTrue(all(result.positives['a'] == ['test', 'here']))
        self.assertTrue(all(result.positives['b'] == [1, 2]))

