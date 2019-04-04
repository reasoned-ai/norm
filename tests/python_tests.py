"""Unit tests for embedding Python code"""
import datetime

from pandas import DataFrame

from tests.utils import NormTestCase


class PythonTestCase(NormTestCase):

    def test_python_declaration(self):
        script = """
        test := {{
            from datetime import datetime
            test = datetime.utcnow
        }};
        """
        self.execute(script)
        lam = self.execute("test;")
        self.assertTrue(lam is not None)

    def test_python_query(self):
        script = """
        test := {{
            from datetime import datetime
            test = datetime.utcnow
        }};
        """
        self.execute(script)
        result = self.execute("test();")
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, datetime.datetime))

    def test_python_query_on_data(self):
        script = """
        test := {{
            import numpy as np
            test = np.sin
        }};
        """
        self.execute(script)
        script = """
        a := (1, 2, 3)
          |  (1.1, 2.2, 3.3)
          |  (0.1, 0.2, 0.3)
          ;
        """
        self.execute(script)
        result = self.execute("test(a());")
        self.assertTrue(result is not None)

    def test_python_custom_function(self):
        script = """
        test := {{
            def test(x):
                return '{}-{}'.format(x.b, x.c)
        }};
        """
        self.execute(script)
        script = """
        a(b:String, c:String) := ("store", "truth")
                              |  ("having", "evil")
                              ;
        """
        self.execute(script)
        result = self.execute("test(a());")
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, DataFrame))

    def test_python_function_projection(self):
        script = """
        utcnow := {{
            from datetime import datetime
            utcnow = datetime.utcnow
        }};
        """
        self.execute(script)
        script = """
        a(b:String, c:String) := ("store", "truth")
                              |  ("having", "evil")
                              ;
        """
        self.execute(script)
        lam = self.execute("a &= utcnow()?time;")
        self.assertTrue(lam is not None)
        self.assertTrue(isinstance(lam.data, DataFrame))
        self.assertTrue(lam.data['time'] is not None)

    def test_python_function_projection2(self):
        script = """
        gaussian := {{
            import numpy as np
            def gaussian(v):
                return np.exp(-v*v / 2)/np.sqrt(2*np.pi)
        }};
        """
        self.execute(script)
        script = """
        a(v: Float, mu: Float) := (1.2, 2.3)
                               |  (1.0, 2.0)
                               ;
        """
        self.execute(script)
        lam = self.execute("a &= gaussian(v)?p;")
        self.assertTrue(lam is not None)
        self.assertTrue(isinstance(lam.data, DataFrame))
        self.assertTrue(lam.data['p'] is not None)
