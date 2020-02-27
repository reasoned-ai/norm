"""Unit tests for Norm"""
from norm.models.variable import Input
from tests.utils import NormTestCase


class EvaluationTestCase(NormTestCase):

    def setUp(self):
        super().setUp()
        self.execute("""
        alarm:: (event: String, ip: String, time: Datetime, tally: Integer)
             := {
                    import pandas as pd
                    pd.read_parquet('./data/norm/packed_alarms.parquet')
                }
        """)

    def test_select_optional_columns(self):
        result = self.execute("alarm")
        self.assertTrue(result is not None)
        var_event = result.lam.get('event')
        var_summary = result.lam.get('summary')
        self.assertTrue(isinstance(var_event, Input) and var_event.as_primary)
        self.assertTrue(isinstance(var_summary, Input) and not var_summary.as_primary)

    def test_select_time_columns(self):
        result = self.execute("alarm:: (event:String, ip:String, time:Datetime:time)")
        self.assertTrue(result is not None)
        var_time = result.lam.get('time')
        self.assertTrue(isinstance(var_time, Input) and var_time.as_time)

    def test_evaluate_oid_generation(self):
        self.execute("test:: (a: String, b: Integer)")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)")
        result = self.execute("test?")
        self.assertTrue(result is not None)
        self.assertTrue(all(result.index == [105841138, 99811799, 145556044]))

    def test_evaluate_oid_generation_ignore_optional_variables(self):
        self.execute("test:: (a: String, b: Integer, c: String: optional)")
        self.execute("test := ('test', 1, 'tt')"
                     "     |  ('here', 2, 'gg')"
                     "     |  ('there', 3, 'hh')")
        result = self.execute("test(c?)?")
        self.assertTrue(result is not None)
        self.assertTrue(result.positives.index.name == 'test')
        self.assertTrue(all(result.positives.index == [105841138, 99811799, 145556044]))
        self.assertTrue(all(result.positives['test.c'] == ['tt', 'gg', 'hh']))

    def test_evaluate_oid_set(self):
        self.execute("test:: (a: String, b: Integer: oid)")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)")
        result = self.execute("test?")
        self.assertTrue(result is not None)
        self.assertTrue(all(result.positives.index == [1, 2, 3]))

    def test_evaluate_empty_as_default(self):
        self.execute("test:: (a: String, b: Integer)")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)")
        result = self.execute("test()")
        self.assertTrue(all(result.positives['a'] == ['']))
        self.assertTrue(all(result.positives['b'] == [0]))

    def test_evaluate_assigned_columns(self):
        result = self.execute("test:: (a: String, b: Integer)")
        self.assertTrue(result.type_ is not None)
        result = self.execute("test('test', 1)")
        self.assertTrue(all(result.positives['a'] == ['test']))
        self.assertTrue(all(result.positives['b'] == [1]))
        result = self.execute("test(['test', 'here'], [1, 2]);")
        self.assertTrue(all(result.positives['a'] == ['test', 'here']))
        self.assertTrue(all(result.positives['b'] == [1, 2]))

    def test_evaluate_assigned_columns_uneven(self):
        self.execute("test:: (a: String, b: Integer)")
        result = self.execute("test := ('test', 1)"
                              "     |  ('here', 2)"
                              "     |  ('there', 3)")
        self.assertTrue(result.type_ is not None)
        result = self.execute("test(['test', 'here'], b=1)")
        self.assertTrue(all(result.positives['a'] == ['test', 'here']))
        self.assertTrue(all(result.positives['b'] == [1, 1]))
        result = self.execute("test(b=1, a=['test', 'here']);")
        self.assertTrue(all(result.positives['a'] == ['test', 'here']))
        self.assertTrue(all(result.positives['b'] == [1, 1]))

    def test_evaluate_assigned_lambda_columns(self):
        self.execute("test2:: String"
                     "     := 'test'"
                     "     |  'here'"
                     "     |  'there'")
        self.execute("test:: (a: test2, b: Integer)")
        result = self.execute("test(a=(test2 like 'here'), b=1)")
        self.assertTrue(all(result.positives['a'] == ['here', 'there']))
        self.assertTrue(all(result.positives['b'] == [1, 1]))

    def test_evaluate_projection(self):
        self.execute("test:: (a: String, b: Integer)")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)")
        result = self.execute("test(a?)")
        self.assertTrue(all(result.positives['a'] == ['test', 'here', 'there']))
        self.assertTrue('b' not in result.type_)

    def test_evaluate_equality_projection(self):
        self.execute("test:: (a: String, b: Integer)")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)")
        result = self.execute("test(a=='here', b?)")
        self.assertTrue(all(result.positives['b'] == [2]))
        self.assertTrue('a' not in result.type_)

    def test_evaluate_conditional_projection(self):
        self.execute("test:: (a: String, b: Integer)")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)")
        result = self.execute("test(a like 'here', b?)")
        self.assertTrue(all(result.positives['b'] == [2, 3]))
        self.assertTrue('a' not in result.type_)
        result = self.execute("test(a like 'here'?, b>2)")
        self.assertTrue(all(result.positives['a'] == ['there']))
        self.assertTrue('b' not in result.type_)

    def test_chained_evaluation(self):
        self.execute("test:: (a: String, b: Integer)")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)")
        result = self.execute("test.a.max")
        self.assertTrue(result.positives['a.max'].values[0] == 'there')
        result = self.execute("test.a.count")
        self.assertTrue(result.positives['a.count'].values[0] == 3)

    def test_chained_str_evaluation(self):
        self.execute("test:: (a: String, b: Integer)")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)")
        result = self.execute("test.a.capitalize")
        self.assertTrue(all(result.positives['a.capitalize'] == ['Test', 'Here', 'There']))
        result = self.execute("test.a.len")
        self.assertTrue(all(result.positives['a.len'] == [4, 4, 5]))
        result = self.execute("test.a.findall('ere')")
        self.assertTrue(all(result.positives['a.findall'] == [[], ['ere'], ['ere']]))
