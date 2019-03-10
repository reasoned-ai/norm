"""Unit tests for Norm"""
from tests.norm.utils import NormTestCase


class VersioningTestCase(NormTestCase):

    def test_same_version_for_draft(self):
        lam = self.execute("version_test(test:Integer);")
        script = """
        // revising a draft has the same version
        version_test(test:Integer, test2:String);
        """
        lam2 = self.execute(script)
        self.assertTrue(lam2.version == lam.version)

    def test_version_up(self):
        self.execute("version_test(test:Integer);")
        lam1 = self.execute("export version_test;")
        self.execute("version_test(test:Integer, test2:String);")
        lam2 = self.execute("export version_test;")
        self.assertTrue(lam2.version > lam1.version)
        self.assertTrue(lam2.cloned_from is lam1)

