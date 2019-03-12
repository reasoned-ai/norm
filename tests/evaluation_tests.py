"""Unit tests for Norm"""
from norm.config import DATA_STORAGE_ROOT
from norm.models import Level, Status
from tests.utils import NormTestCase


class EvaluationTestCase(NormTestCase):

    def test_read_data(self):
        self.execute("wikisql(phase:Integer);")
        lam = self.execute("wikisql.read('./data/norm/tmp/wikisql/train.jsonl', ext='jsonl');")
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
                                                           lam.version[1:].replace('-', '')))

    def test_ignore_same_revision(self):
        self.execute("wikisql(phase: Integer);")
        lam = self.execute("wikisql.read('./data/norm/tmp/wikisql/train.jsonl', ext='jsonl');")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 2)
        lam2 = self.execute("wikisql.read('./data/norm/tmp/wikisql/train.jsonl', ext='jsonl');")
        self.assertTrue(lam is lam2)
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(len(lam.data) > 0)

    def test_recognize_repeated_declaration_within_the_same_session(self):
        script = """
        Company(name: String, description: String, founders: [String], founded_at: Datetime);
        """
        company = self.execute(script)
        assert(company is not None)

        new_company = self.execute(script)
        assert(company is new_company)
