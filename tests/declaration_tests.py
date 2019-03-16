"""Unit tests for Norm"""
from tests.utils import NormTestCase


class DeclarationTestCase(NormTestCase):

    def test_recognize_declaration(self):
        script = """
        Company(name: String, description: String, founders: [String], founded_at: Datetime);
        """
        lam = self.execute(script)
        self.assertTrue(lam is not None)

    def test_recognize_repeated_declaration_within_the_same_session(self):
        script = """
        Company(name: String, mission: String, founders: [String], founded_at: Datetime);
        """
        company = self.execute(script)
        self.assertTrue(company is not None)

        new_company = self.execute(script)
        self.assertTrue(company is new_company)

    def test_declaration_function(self):
        lam = self.execute("test: String;")
        self.assertTrue(lam.get_type(lam.VAR_OUTPUT).name == 'String')

    def test_none_declaration(self):
        lam = self.execute("test;")
        self.assertTrue(lam is None)
