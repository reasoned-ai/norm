"""Unit tests for Norm"""
from tests.utils import NormTestCase


class VersioningTestCase(NormTestCase):

    def test_version_declaration(self):
        res1 = self.execute("version_test:: (test: Integer)")
        res2 = self.execute("""
            # revising leads to a different version
            version_test:: (test: Integer, test2: String)
        """)
        self.assertTrue(res1.type_.version != res2.type_.version)

    def test_version_export(self):
        self.execute("""
            version_test:: (test: Integer)
            export version_test as version_test$1 to norm.test.version

            version_test:: (test: Integer, test2: String)
            export version_test as version_test$2 to norm.test.version
        """)
        res1 = self.execute("""
            import norm.test.version.version_test$1 as vt1
        """)
        res2 = self.execute("""
            import norm.test.version.version_test$2 as vt1
        """)
        self.assertTrue(res1.type_.version != res2.type_.version)

