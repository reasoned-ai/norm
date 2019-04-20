"""Unit tests for Norm"""
from tests.utils import NormTestCase
from norm.config import DATA_STORAGE_ROOT
from norm.models import Status
import os


class EvaluationTestCase(NormTestCase):

    def test_read_jsonl(self):
        self.execute("wikisql(phase:Integer);")
        data = self.execute("wikisql.read('./data/norm/wikisql/train.jsonl', ext='jsonl');")
        lam = self.execute("wikisql;")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(lam.end_of_revisions)
        self.assertTrue(not lam.empty_revisions)
        self.assertTrue(data is not None)
        self.assertTrue(lam.current_revision == len(lam.revisions) - 1)
        self.assertTrue(lam.queryable)
        self.assertTrue(lam.status == Status.DRAFT)
        self.assertTrue(lam.nargs > 1)
        self.assertTrue(lam.folder == '{}/{}/{}/{}'.format(DATA_STORAGE_ROOT,
                                                           lam.namespace.replace('.', '/'),
                                                           lam.name,
                                                           lam.version))

    def test_read_parquet(self):
        self.execute("alarms(event:String);")
        data = self.execute("alarms.read('./data/norm/packed_alarms.parquet', ext='parq');")
        lam = self.execute("alarms;")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(lam.end_of_revisions)
        self.assertTrue(not lam.empty_revisions)
        self.assertTrue(data is not None)
        self.assertTrue(len(data) > 0)
        self.assertTrue(lam.current_revision == len(lam.revisions) - 1)
        self.assertTrue(lam.queryable)
        self.assertTrue(lam.status == Status.DRAFT)
        self.assertTrue(lam.nargs > 1)
        self.assertTrue(lam.folder == '{}/{}/{}/{}'.format(DATA_STORAGE_ROOT,
                                                           lam.namespace.replace('.', '/'),
                                                           lam.name,
                                                           lam.version))

    def test_ignore_same_revision(self):
        self.execute("wikisql(phase: Integer);")
        data = self.execute("wikisql.read('./data/norm/wikisql/train.jsonl', ext='jsonl');")
        lam = self.execute("wikisql;")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 2)
        data2 = self.execute("wikisql.read('./data/norm/wikisql/train.jsonl', ext='jsonl');")
        self.assertTrue(len(data) == len(data2))
        self.assertTrue(len(lam.data[lam.VAR_OID]) > 0)

    def test_recognize_repeated_declaration_within_the_same_session(self):
        script = """
        Company(name: String, description: String, founders: [String], founded_at: Datetime);
        """
        company = self.execute(script)
        self.assertTrue(company is not None)

        new_company = self.execute(script)
        self.assertTrue(company is new_company)

    def test_save_lambda_with_data_after_commit(self):
        self.execute("wikisql(phase:Integer);")
        self.execute("wikisql.read('./data/norm/wikisql/train.jsonl', ext='jsonl');")
        self.session.commit()
        lam = self.execute("wikisql;")
        self.assertTrue(os.path.exists(lam.folder))

    def test_evaluate_oid_generation(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        results = self.execute("test?;")
        self.assertTrue(results is not None)
        self.assertTrue(all(results['test'] == [73204161, 68944293, 107020825]))

    def test_evaluate_oid_generation_ignore_optional_variables(self):
        self.execute("test(a: String, b: Integer, c: String: optional);")
        self.execute("test := ('test', 1, 'tt')"
                     "     |  ('here', 2, 'gg')"
                     "     |  ('there', 3, 'hh')"
                     "     ;")
        results = self.execute("test(c?)?;")
        self.assertTrue(results is not None)
        self.assertTrue(all(results['test'] == [73204161, 68944293, 107020825]))
        self.assertTrue(all(results['test.c'] == ['tt', 'gg', 'hh']))

    def test_evaluate_empty_as_default(self):
        self.execute("test(a: String, b: Integer);")
        test = self.execute("test;")
        self.assertTrue(test is not None)
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test();")
        self.assertTrue(all(data['a'] == ['']))
        self.assertTrue(all(data['b'] == [0]))

    def test_evaluate_assigned_columns(self):
        self.execute("test(a: String, b: Integer);")
        test = self.execute("test;")
        self.assertTrue(test is not None)
        data = self.execute("test('test', 1);")
        self.assertTrue(data is not test)
        self.assertTrue(all(data['a'] == ['test']))
        self.assertTrue(all(data['b'] == [1]))
        data = self.execute("test(['test', 'here'], [1, 2]);")
        self.assertTrue(all(data['a'] == ['test', 'here']))
        self.assertTrue(all(data['b'] == [1, 2]))

    def test_evaluate_assigned_columns_uneven(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        test = self.execute("test;")
        self.assertTrue(test is not None)
        data = self.execute("test(['test', 'here'], b=1);")
        self.assertTrue(all(data['a'] == ['test', 'here']))
        self.assertTrue(all(data['b'] == [1, 1]))
        data = self.execute("test(b=1, a=['test', 'here']);")
        self.assertTrue(all(data['a'] == ['test', 'here']))
        self.assertTrue(all(data['b'] == [1, 1]))

    def test_evaluate_assigned_lambda_columns(self):
        self.execute("test2: String;")
        self.execute("test2 := ('test')"
                     "      |  ('here')"
                     "      |  ('there')"
                     "      ;")
        self.execute("test(a: test2, b: Integer);")
        data = self.execute("test(a=test2?, b=1);")
        self.assertTrue(all(data['a'] == ['test', 'here', 'there']))
        self.assertTrue(all(data['b'] == [1, 1, 1]))

    def test_evaluate_projection(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test(a?);")
        self.assertTrue(all(data['a'] == ['test', 'here', 'there']))
        self.assertTrue('b' not in data.columns)

    def test_evaluate_equality_projection(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test(a=='here', b?);")
        self.assertTrue(all(data['b'] == [2]))
        self.assertTrue('a' not in data.columns)

    def test_evaluate_conditional_projection(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test(a~'here', b?);")
        self.assertTrue(all(data['b'] == [2, 3]))
        self.assertTrue('a' not in data.columns)
        data = self.execute("test(a~'here'?, b>2);")
        self.assertTrue(all(data['a'] == ['there']))
        self.assertTrue('b' not in data.columns)

    def test_chained_evaluation(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test.a.max();")
        self.assertTrue(data == 'there')
        data = self.execute("test.a.count();")
        self.assertTrue(data == 3)

    def test_chained_str_evaluation(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        data = self.execute("test.a.capitalize();")
        self.assertTrue(all(data == ['Test', 'Here', 'There']))
        data = self.execute("test.a.len();")
        self.assertTrue(all(data == [4, 4, 5]))
        data = self.execute("test.a.findall('ere');")
        self.assertTrue(all(data == [[], ['ere'], ['ere']]))
