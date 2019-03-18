"""Unit tests for Arithmetic expressions"""
from norm.config import DATA_STORAGE_ROOT
from norm.models import Level, Status
from tests.utils import NormTestCase


class ArithmeticTestCase(NormTestCase):

    def test_arithmetic_evaluation(self):
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
