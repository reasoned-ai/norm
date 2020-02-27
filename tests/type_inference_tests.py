"""Unit tests for Implementation"""
from norm.models import store
from tests.utils import NormTestCase


class TypeInferenceTestCase(NormTestCase):

    def test_anonymous_implementation(self):
        script = """
            student
            :: (id: String, name: String, department_name: String, total_credits: Float) 
            := { 
                import sqlite3
                import pandas as pd            
                conn = 'sqlite:///data/college_2.sqlite'
                pd.read_sql('SELECT * FROM student;', conn).rename(
                    columns={'ID': 'id', 
                             'name': 'name', 
                             'dept_name': 'department_name', 
                             'tot_cred': 'total_credits'}                
                )
               }
            
            tmp := student(id?, name?, department_name?, total_credits>10?)
        """
        result = self.execute(script)
        self.assertTrue(result.lam.name == 'tmp')
        self.assertTrue(result.lam.get('id').type_ == store.String)
        self.assertTrue(result.lam.get('name').type_ == store.String)
        self.assertTrue(result.lam.get('department_name').type_ == store.String)
        self.assertTrue(result.lam.get('total_credits').type_ == store.Float)
