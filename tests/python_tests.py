"""Unit tests for embedding Python code"""
import datetime

from norm.models.norm import PythonLambda
from norm.models.variable import Variable
from tests.utils import NormTestCase


class PythonTestCase(NormTestCase):

    def test_python_declaration(self):
        script = """
        test
        :: Datetime
        := {
            from datetime import datetime
            return datetime.now()
        }
        """
        result = self.execute(script)
        self.assertTrue(result.type_ is not None)
        self.assertTrue(isinstance(result.type_, PythonLambda))

    def test_python_query(self):
        script = """
        test
        :: Datetime
        := {
            from datetime import datetime
            return datetime.now()
        }
        
        test()
        """
        result = self.execute(script)
        self.assertTrue(isinstance(result.positives[f"{Variable.VAR_ANONYMOUS_STUB}0"].values[0],
                                   datetime.datetime))

    def test_python_query_on_data(self):
        script = """
        test
        :: (v: Float) -> Float
        := {
            import numpy as np
            return np.sin(v)
        }
        
        a :=  1 | 1.1 | 2.3
        
        test(a)
        """
        result = self.execute(script)
        self.assertTrue(not result.positives.empty)

    def test_python_custom_function(self):
        script = """
        a
        :: (b: String, c: String)
        := ('store', 'truth')
         | ('having', 'evil')


        test
        :: (x: a) -> String
        := {
            return x.b.str.cat(x.c)
        }
        
         
        a.test()
        """
        result = self.execute(script)
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)

    def test_python_function_projection(self):
        script = """
        utcnow
        :: Datetime
        := {
            from datetime import datetime
            return datetime.now()
        }

        a
        :: (b: String, c: String)
        := ('store', 'truth')
         | ('having', 'evil')
        
        a &= utcnow() as time        
        """
        result = self.execute(script)
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue(len(result.positives['time']) == 2)

    def test_python_function_projection2(self):
        script = """
        gaussian
        :: (v: Float) -> Float
        := {
            import numpy as np
            return np.exp(-v*v / 2)/np.sqrt(2*np.pi)
        }

        a
        :: (v: Float, mu: Float)
        := (1.2, 2.3)
         | (1.0, 2.0)
        
        a &= gaussian(v) as p        
        """
        result = self.execute(script)
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives['p'].empty)

    def test_python_code_expression(self):
        import pandas as pd
        t1 = pd.DataFrame(data={'a': ['a', 'b', 'c'], 'b': [1, 2, 3]})
        result = self.execute("test:: (a: String, b: Integer) := { t1 }")
        self.assertTrue(result.type_ is not None)
        self.assertTrue(all(result.positives['a'] == ['a', 'b', 'c']))
        self.assertTrue(all(result.positives['b'] == [1, 2, 3]))
