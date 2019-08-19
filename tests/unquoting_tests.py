"""Unit tests for Norm"""
from tests.utils import NormTestCase


class UnquotingTestCase(NormTestCase):

    def test_dynamic_projection(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        query = """
        with(test), [('(.*)s', 's'), ('(.*)e', 'e'), ('th(.*)', 'th')]?(p,n) & extract(p, a)?pattern_{n};
        """
        data = self.execute(query)
        self.assertTrue(data is not None)
        self.assertTrue(all(data['pattern_e'].dropna() == ['t', 'her', 'ther']))
        self.assertTrue(all(data['pattern_s'].dropna() == ['te']))
        self.assertTrue(all(data['pattern_th'].dropna() == ['ere']))

    def test_single_exist_context(self):
        self.execute("tmp := read('./data/norm/packed_alarms.parquet', ext='parq');")
        self.execute("alarms(event:String, ip:String, time:Datetime, tally:Integer);")
        self.execute("alarms := tmp(event?, ip?, time?, tally?);")
        result = self.execute("with(alarms), foreach(event, ip), tally.sum() > 1000 ?event_{event};")
        self.assertTrue(result is not None)
        self.assertTrue(len(result.columns) == 16)
