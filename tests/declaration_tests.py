"""Unit tests for Norm"""
from tests.utils import NormTestCase


class DeclarationTestCase(NormTestCase):

    def test_recognize_declaration(self):
        result = self.execute("""
        Company:: (name: String, description: String, founders: [String], founded_at: Datetime)
        """)
        self.assertTrue(result is not None)
        self.assertTrue(result.type_ is not None)

    def test_recognize_repeated_declaration_within_the_same_session(self):
        script = """
        Company:: (name: String, mission: String, founders: [String], founded_at: Datetime)
        """
        company = self.execute(script)
        self.assertTrue(company is not None)

        new_company = self.execute(script)
        self.assertTrue(company.type_ == new_company.type_)

