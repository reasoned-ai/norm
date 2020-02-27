"""Unit tests for Joining Lambdas"""
from tests.utils import NormTestCase


class JoinLambdaTestCase(NormTestCase):

    def test_access_join(self):
        script = """
        Class:: (name: String, level: Integer)
        Teacher:: (name: String)
        
        teach
        :: (teacher: Teacher, class: Class)
        := ('joe',   ('mathematics', 101))
         | ('alice', ('history', 101))
         | ('bob',   ('literature', 101))
         | ('joe',   ('computer science', 101))
         | ('alice', ('mathematics', 201))
        
        teach(teacher?, class.name=='mathematics') 
        """
        result = self.execute(script)
        self.assertTrue(result is not None)
        self.assertTrue(all(result.positives['teacher'] == [42205503, 100663807]))

    def test_combined_join(self):
        script = """
        Event
        :: (name: String, ip: String)
        := ('Windows crash', '192.168.0.1')
         | ('Windows crash', '192.168.0.102')
         | ('Unix crash', '192.168.0.2')
         | ('Unix crash', '192.168.0.11')
         | ('Windows crash', '192.168.0.3')
         
        Cluster
        :: (name: String, ip: String)
        := ('Application cluster', '192.168.0.11')
         | ('Application cluster', '192.168.0.2')
         | ('Oracle cluster', '192.168.0.1')
         | ('Oracle cluster', '192.168.0.3')
         | ('Oracle cluster', '192.168.0.102')
         
        Event(name?, ip? as eip) & Cluster(ip=eip, name like 'App'? as cluster_name)
        """
        results = self.execute(script)
        self.assertTrue(len(results) == 2)

    def test_combined_join_multiple(self):
        script = """
        Event
        :: (name: String, ip: String)
        := ('Windows crash', '192.168.0.1')
         | ('Windows crash', '192.168.0.102')
         | ('Unix crash', '192.168.0.2')
         | ('Unix crash', '192.168.0.11')
         | ('Windows crash', '192.168.0.3')

        Cluster
        :: (name: String, ip: String)
        := ('Application cluster', '192.168.0.11')
         | ('Application cluster', '192.168.0.2')
         | ('Oracle cluster', '192.168.0.1')
         | ('Oracle cluster', '192.168.0.3')
         | ('Oracle cluster', '192.168.0.102')

        Application
        :: (name: String, cluster: String)
        := ('Menu', 'Application cluster')
         | ('Report', 'Application cluster')
         | ('Traffic', 'Application cluster')
         | ('Oracle server', 'Oracle cluster')
         | ('Oracle monitor', 'Oracle cluster')
         
        Event(name?, ip? as eip)
         and Cluster(ip=eip, name like 'App'? as cluster_name)
         and Application(cluster=cluster_name, name?application_name)
        """
        results = self.execute(script)
        self.assertTrue(len(results) > 2)
