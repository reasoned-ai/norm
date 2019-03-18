"""Unit tests for Norm"""
from tests.utils import NormTestCase
from norm.config import DATA_STORAGE_ROOT
from norm.models import Level, Status
import os


class EvaluationTestCase(NormTestCase):

    def test_read_jsonl(self):
        self.execute("wikisql(phase:Integer);")
        lam = self.execute("wikisql.read('./data/norm/wikisql/train.jsonl', ext='jsonl');")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(lam.end_of_revisions)
        self.assertTrue(not lam.empty_revisions)
        self.assertTrue(lam.data is not None)
        self.assertTrue(lam.current_revision == len(lam.revisions) - 1)
        self.assertTrue(lam.level == Level.QUERYABLE)
        self.assertTrue(lam.status == Status.DRAFT)
        self.assertTrue(lam.nargs > 1)
        self.assertTrue(lam.folder == '{}/{}/{}/{}'.format(DATA_STORAGE_ROOT,
                                                           lam.namespace.replace('.', '/'),
                                                           lam.name,
                                                           lam.version))

    def test_read_parquet(self):
        self.execute("alarms(event:String);")
        lam = self.execute("alarms.read('./data/norm/packed_alarms.parquet', ext='parq');")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(lam.end_of_revisions)
        self.assertTrue(not lam.empty_revisions)
        self.assertTrue(lam.data is not None)
        self.assertTrue(lam.current_revision == len(lam.revisions) - 1)
        self.assertTrue(lam.level == Level.QUERYABLE)
        self.assertTrue(lam.status == Status.DRAFT)
        self.assertTrue(lam.nargs > 1)
        self.assertTrue(lam.folder == '{}/{}/{}/{}'.format(DATA_STORAGE_ROOT,
                                                           lam.namespace.replace('.', '/'),
                                                           lam.name,
                                                           lam.version))

    def test_ignore_same_revision(self):
        self.execute("wikisql(phase: Integer);")
        lam = self.execute("wikisql.read('./data/norm/wikisql/train.jsonl', ext='jsonl');")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 2)
        lam2 = self.execute("wikisql.read('./data/norm/wikisql/train.jsonl', ext='jsonl');")
        self.assertTrue(lam is lam2)
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(len(lam.data) > 0)
        self.assertTrue(len(lam.df[lam.VAR_OID]) > 0)

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

    def test_evaluate_empty(self):
        self.execute("test(a: String, b: Integer);")
        test = self.execute("test;")
        self.assertTrue(test is not None)
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        lam = self.execute("test();")
        self.assertTrue(lam is not test)
        self.assertTrue(lam.variables == test.variables)
        self.assertTrue(all(lam.data['a'] == ['test', 'here', 'there']))
        self.assertTrue(all(lam.data['b'] == [1, 2, 3]))

    def test_evaluate_assigned_columns(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        test = self.execute("test;")
        self.assertTrue(test is not None)
        lam = self.execute("test('test', 1);")
        self.assertTrue(lam is not test)
        self.assertTrue(lam.variables == test.variables)
        self.assertTrue(all(lam.data['a'] == ['test']))
        self.assertTrue(all(lam.data['b'] == [1]))
        lam = self.execute("test(['test', 'here'], [1, 2]);")
        self.assertTrue(all(lam.data['a'] == ['test', 'here']))
        self.assertTrue(all(lam.data['b'] == [1, 2]))

    def test_evaluate_assigned_columns_uneven(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        test = self.execute("test;")
        self.assertTrue(test is not None)
        lam = self.execute("test(['test', 'here'], b=1);")
        self.assertTrue(all(lam.data['a'] == ['test', 'here']))
        self.assertTrue(all(lam.data['b'] == [1, 1]))
        lam = self.execute("test(b=1, a=['test', 'here']);")
        self.assertTrue(all(lam.data['a'] == ['test', 'here']))
        self.assertTrue(all(lam.data['b'] == [1, 1]))

    def test_evaluate_assigned_lambda_columns(self):
        self.execute("test2: String;")
        self.execute("test2 := ('test')"
                     "      |  ('here')"
                     "      |  ('there')"
                     "      ;")
        self.execute("test(a: test2, b: Integer);")
        lam = self.execute("test(a=test2(), b=1);")
        self.assertTrue(all(lam.data['a'] == ['test', 'here', 'there']))
        self.assertTrue(all(lam.data['b'] == [1, 1, 1]))

    def test_evaluate_projection(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        lam = self.execute("test(a?);")
        self.assertTrue(lam is not None)
        self.assertTrue(all(lam.data['a'] == ['test', 'here', 'there']))
        self.assertTrue('b' not in lam.data.columns)

    def test_evaluate_equality_projection(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        lam = self.execute("test(a=='here', b?);")
        self.assertTrue(lam is not None)
        self.assertTrue(all(lam.data['b'] == [2]))
        self.assertTrue('a' not in lam.data.columns)

    def test_evaluate_conditional_projection(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        lam = self.execute("test(a~'here', b?);")
        self.assertTrue(lam is not None)
        self.assertTrue(all(lam.data['b'] == [2, 3]))
        self.assertTrue('a' not in lam.data.columns)
        lam = self.execute("test(a~'here'?, b>2);")
        self.assertTrue(lam is not None)
        self.assertTrue(all(lam.data['a'] == ['there']))
        self.assertTrue('b' not in lam.data.columns)

    def test_chained_evaluation(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        lam = self.execute("test.a.max();")
        self.assertTrue(lam is not None)
        self.assertTrue(lam.data == 'there')
        lam = self.execute("test.a.count();")
        self.assertTrue(lam is not None)
        self.assertTrue(lam.data == 3)

    def test_chained_str_evaluation(self):
        self.execute("test(a: String, b: Integer);")
        self.execute("test := ('test', 1)"
                     "     |  ('here', 2)"
                     "     |  ('there', 3)"
                     "     ;")
        lam = self.execute("test.a.capitalize();")
        self.assertTrue(all(lam.data == ['Test', 'Here', 'There']))
        lam = self.execute("test.a.len();")
        self.assertTrue(all(lam.data == [4, 4, 5]))
        lam = self.execute("test.a.findall('ere');")
        self.assertTrue(all(lam.data == [[], ['ere'], ['ere']]))
