"""Unit tests for Norm"""
from tests.utils import NormTestCase
from norm.models import Status


class NamespaceTestCase(NormTestCase):

    def test_importing(self):
        self.execute("import norm.test.*;")
        self.assertTrue('norm.test' in self.executor.search_namespaces)

    def test_importing_type(self):
        self.execute("Tester(dummy:Integer);")
        self.execute("export Tester norm.test;")
        lam = self.execute("import norm.test.Tester;")
        self.assertTrue('norm.test' in self.executor.search_namespaces)
        self.assertTrue(lam is not None)
        self.assertTrue(lam.namespace == 'norm.test')

    def test_renaming(self):
        self.execute("Tester(dummy:Integer);")
        self.execute("export Tester norm.test;")
        lam = self.execute("import norm.test.Tester as tt;")
        self.assertTrue('norm.test' in self.executor.search_namespaces)
        self.assertTrue(lam is not None)
        self.assertTrue(lam.namespace == self.executor.context_namespace)
        self.assertTrue(lam.name == 'tt')

    def test_exporting(self):
        self.execute("Tester(dummy:Integer);")
        lam = self.execute("export Tester norm.test2 as Tester2;")
        self.assertTrue(lam is not None)
        self.assertTrue(lam.namespace == 'norm.test2')
        self.assertTrue(lam.name == 'Tester2')

    def test_exporting_default(self):
        self.execute("Tester(dummy:Integer);")
        lam = self.execute("export Tester;")
        self.assertTrue(lam is not None)
        self.assertTrue(lam.namespace == self.executor.user_namespace)
        self.assertTrue(lam.name == 'Tester')

    def test_exporting_a_version(self):
        lam = self.execute("Tester(dummy:Integer);")
        lam = self.execute("export Tester{} norm.test3;".format(lam.version))
        self.assertTrue(lam is not None)
        self.assertTrue(lam.namespace == "norm.test3")
        self.assertTrue(lam.name == 'Tester')
        self.assertTrue(lam.status == Status.READY)
        lam = self.execute("Tester;")
        self.assertTrue(lam is not None)
        self.assertTrue(lam.namespace == self.executor.context_namespace)
        self.assertTrue(lam.status == Status.DRAFT)

