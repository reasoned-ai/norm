"""Unit tests for Norm"""
from tests.norm.utils import NormTestCase


class EvaluationTestCase(NormTestCase):

    def test_read_data(self):
        self.execute("wikisql(phase:Integer);")
        lam = self.execute("wikisql.read('./data/norm/tmp/wikisql/train.jsonl', ext='jsonl');")
        self.assertTrue(lam is not None)

    def test_recognize_repeated_declaration_within_the_same_session(self):
        script = """
        Company(name: String, description: String, founders: [String], founded_at: Datetime);
        """
        company = self.execute(script)
        assert(company is not None)

        new_company = self.execute(script)
        assert(company.id == new_company.id)
