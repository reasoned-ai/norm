"""Unit tests for Implementation"""
from norm.models import norma
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
        self.assertTrue(result.type_.name == 'tmp')
        self.assertTrue(result.type_.get('id').type_ == norma.native.String.latest)
        self.assertTrue(result.type_.get('name').type_ == norma.native.String.latest)
        self.assertTrue(result.type_.get('department_name').type_ == norma.native.String.latest)
        self.assertTrue(result.type_.get('total_credits').type_ == norma.native.Float.latest)
