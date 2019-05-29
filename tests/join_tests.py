"""Unit tests for Joining Lambdas"""
from tests.utils import NormTestCase


class JoinLambdaTestCase(NormTestCase):

    def test_join(self):
        self.execute("Class(name: String, level: Integer);")
        self.execute("Teacher(name: String);")
        self.execute("teach(teacher: Teacher, class: Class);")
        self.execute("teach := (Teacher('joe'), Class('mathematics', 101))"
                     "      |  (Teacher('alice'), Class('history', 101))"
                     "      |  (Teacher('bob'), Class('literature', 101))"
                     "      |  (Teacher('joe'), Class('computer science', 101))"
                     "      |  (Teacher('alice'), Class('mathematics', 201))"
                     "      ;")
        results = self.execute("teach(teacher?, class.name=='mathematics');")
        self.assertTrue(results is not None)
        self.assertTrue(all(results['teacher'] == [42205503, 100663807]))

    def test_combined_join(self):
        self.execute("Event(name: String, ip: String);")
        self.execute("Event := ('Windows crash', '192.168.0.1')"
                     "       | ('Windows crash', '192.168.0.102')"
                     "       | ('Unix crash', '192.168.0.2')"
                     "       | ('Unix crash', '192.168.0.11')"
                     "       | ('Windows crash', '192.168.0.3');")
        self.execute("Cluster(name: String, ip: String);")
        self.execute("Cluster := ('Application cluster', '192.168.0.11')"
                     "         | ('Application cluster', '192.168.0.2')"
                     "         | ('Oracle cluster', '192.168.0.1')"
                     "         | ('Oracle cluster', '192.168.0.3')"
                     "         | ('Oracle cluster', '192.168.0.102');")
        results = self.execute("Event(name?, ip?eip) & Cluster(ip=eip, name~'App'?cluster_name);")
        self.assertTrue(len(results) == 2)

