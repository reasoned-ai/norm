"""Unit tests for Norm"""
from tests.utils import NormTestCase


class NamespaceTestCase(NormTestCase):

    def setUp(self):
        super().setUp()
        script = """
        Tester:: (dummy: Integer)
        
        export Tester to norm.test
        """
        self.execute(script)

    def test_import(self):
        result = self.execute("import norm.test.*")
        self.assertTrue(result.lam is not None)
        self.assertTrue(result.lam.name == 'Tester')
        self.assertTrue(result.lam.module.name == 'norm.test')

    def test_import_from(self):
        result = self.execute("import Tester from norm.test")
        self.assertTrue(result.lam is not None)
        self.assertTrue(result.lam.name == 'Tester')
        self.assertTrue(result.lam.module.name == 'norm.test')

    def test_renaming(self):
        result = self.execute("import Tester as tt from norm.test.Tester")
        self.assertTrue(result.lam is not None)
        self.assertTrue(result.lam.name == 'tt')
        self.assertTrue(result.lam.module.name == 'norm.test')

    def test_exporting_default(self):
        # TODO should allow user to set the default namespace
        pass

    def test_exporting_a_version(self):
        result = self.execute("Tester:: (dummy:Integer) -> String")
        result = self.execute(f"export Tester${result.lam.version} to norm.test3")
        self.assertTrue(result.lam is not None)
        self.assertTrue(result.lam.module.name == "norm.test3")

