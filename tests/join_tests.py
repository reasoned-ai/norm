"""Unit tests for Joining Lambdas"""
from tests.utils import NormTestCase


class JoinLambdaTestCase(NormTestCase):

    def test_join(self):
        self.execute("Class(name: String, level: Integer);")
        self.execute("Teacher(name: String);")
        self.execute("teach(teacher: Teacher, class: Class);")
        self.execute("Class := ('mathematics', 101)"
                     "      |  ('literature', 101)"
                     "      |  ('history', 101)"
                     "      |  ('mathematics', 201)"
                     "      |  ('computer science', 101)"
                     "      ;")
        self.execute("Teacher := ('joe')"
                     "        |  ('alice')"
                     "        |  ('bob')"
                     "        |  ('carl')"
                     "        ;")
        self.execute("teach := (Teacher('joe'), Class('mathematics', 101))"
                     "      |  (Teacher('alice'), Class('history', 101))"
                     "      |  (Teacher('bob'), Class('literature', 101))"
                     "      |  (Teacher('joe'), Class('computer science', 101))"
                     "      |  (Teacher('alice'), Class('mathematics', 201))"
                     "      ;")
        results = self.execute("teach(teacher?, class.name=='mathematics');")
        self.assertTrue(results is not None)
        self.assertTrue(all(results['teacher'] == ['joe', 'alice']))
