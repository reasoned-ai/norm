"""Unit tests for Norm"""
from tests.norm.utils import NormTestCase


class DeclarationTestCase(NormTestCase):

    def test_recognize_declaration(self):
        script = """
        Company(name: String, description: String, founders: [String], founded_at: Datetime);
        """
        lam = self.execute(script)
        self.assertTrue(lam is not None)

    def test_recognize_repeated_declaration_within_the_same_session(self):
        script = """
        Company(name: String, description: String, founders: [String], founded_at: Datetime);
        """
        company = self.execute(script)
        assert(company is not None)

        new_company = self.execute(script)
        assert(company.id == new_company.id)

