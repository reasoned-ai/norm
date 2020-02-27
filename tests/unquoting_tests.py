"""Unit tests for Norm"""
from tests.utils import NormTestCase


class UnquotingTestCase(NormTestCase):

    def setUp(self):
        super().setUp()
        self.execute("""
        test
        :: (a: String, b: Integer)
        := ('test', 1)
         | ('here', 2)
         | ('there', 3)
        """)

    def test_dynamic_projection(self):
        script = """
           [('(.*)s', 's'), ('(.*)e', 'e'), ('th(.*)', 'th')] as (p,n) 
         & test.a.extract(p) as f'pattern_{n}'
        """
        result = self.execute(script)
        self.assertTrue(result is not None)
        self.assertTrue(all(result.positives['pattern_e'].dropna() == ['t', 'her', 'ther']))
        self.assertTrue(all(result.positives['pattern_s'].dropna() == ['te']))
        self.assertTrue(all(result.positives['pattern_th'].dropna() == ['ere']))

    def test_single_exist_context(self):
        script = """
        alarm
        :: (event: String, ip: String, time: Datetime, tally: Integer)
        := {
            import pandas as pd
            pd.read_parquet('./data/norm/packed_aarms.parquet')
        }
        
        for event, ip in alarm:
            tally.sum > 1000 as f'event_{event}'
        """
        result = self.execute(script)
        self.assertTrue(result is not None)
        self.assertTrue(len(result.lam.bindings) == 16)

    def test_dynamic_code_execution(self):
        self.execute("test:: (a: Integer, b: String)")
        self.execute("test := (1, 'test(a > 1?)')"
                     "     |  (2, 'test(a > 2?)')"
                     "     |  (3, 'test(a > 3?)')")
        result = self.execute("r = f'{test.b}'")
        self.assertTrue(result is not None)
        self.assertTrue(len(result) == 3)
