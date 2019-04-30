"""Unit tests for Arithmetic expressions"""
from tests.utils import NormTestCase


class ArithmeticTestCase(NormTestCase):

    def test_arithmetic_evaluation(self):
        self.execute("test(a: Integer, b: Float);")
        lam = self.execute("test := (2, 3.0)"
                           "     |  (1, 4.2);")
        self.assertTrue(lam is not None)
        lam = self.execute("test &= (a + b) * b ?c;")
        import numpy as np
        self.assertTrue(all(np.abs(lam.data['c'] - [15.00, 21.84]) < 1e-8))
