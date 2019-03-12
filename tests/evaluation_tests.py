"""Unit tests for Norm"""
import os

from norm.config import DATA_STORAGE_ROOT
from norm.models import Level, Status, Lambda
from tests.utils import NormTestCase


class EvaluationTestCase(NormTestCase):

    def test_read_data(self):
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

    def test_ignore_same_revision(self):
        self.execute("wikisql(phase: Integer);")
        lam = self.execute("wikisql.read('./data/norm/wikisql/train.jsonl', ext='jsonl');")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 2)
        lam2 = self.execute("wikisql.read('./data/norm/wikisql/train.jsonl', ext='jsonl');")
        self.assertTrue(lam is lam2)
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(len(lam.data) > 0)

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

