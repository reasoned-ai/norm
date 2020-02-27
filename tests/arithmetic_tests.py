"""Unit tests for Arithmetic expressions"""
from tests.utils import NormTestCase


class ArithmeticTestCase(NormTestCase):

    def test_arithmetic_evaluation(self):
        rt = self.execute("""
        test
          :: (a: Integer, b: Float)
          := 2, 3.0
           | 1, 4.2
        
        test &= c = (a + b) * b
        
        test.c == [15.00, 21.84] 
        """)

        self.assertTrue(rt.negatives.empty)

    def test_arithmetic_evaluation2(self):
        rt = self.execute("""
        test
          :: (a: Integer, b: Float)
          := 2, 3.0
           | 1, 4.2
           
        test &= a - b as c
        
        test.c == [-1.0, -3.2]
        """)
        self.assertTrue(rt.negatives.empty)

    def test_arithmetic_subtraction(self):
        rt = self.execute("""
        test
          :: (a: Integer, b: Float)
          := 2, 3.0
           | 1, 4.2
        
        test &= c = -b
        
        test.c == [-3.0, -4.2]
        """)
        self.assertTrue(rt.negatives.empty)
