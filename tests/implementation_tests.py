"""Unit tests for Implementation"""
from tests.utils import NormTestCase
from norm.models import Lambda, lambdas, AddVariableRevision, RetypeVariableRevision, RenameVariableRevision
from norm.utils import hash_df
from pandas import DataFrame


class ImplementationTestCase(NormTestCase):

    def test_add_data(self):
        self.execute("test(a: Integer, b: String);")
        lam = self.execute("test := (1, 'sf')"
                           "     |  (2, 'sfs')"
                           "     |  (4, 'fs')"
                           "     ;")
        self.assertTrue(lam is not None)
        df = DataFrame(data={'a': [1, 2, 4],
                             'b': ['sf', 'sfs', 'fs']},
                       columns=['a', 'b'])[['a', 'b']]
        self.assertTrue(len(lam.revisions) == 1)
        self.assertTrue(lam.revisions[0].query == hash_df(df))

    def test_add_data_and_declare(self):
        lam = self.execute("test := (1, 'sf')"
                           "     |  (2, 'sfs')"
                           "     |  (4, 'fs')"
                           "     ;")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(lam.variables[0].name == '{}0'.format(Lambda.VAR_ANONYMOUS_STUB))
        self.assertTrue(lam.variables[1].name == '{}1'.format(Lambda.VAR_ANONYMOUS_STUB))
        self.assertTrue(lam.variables[0].type_ == lambdas.Integer)
        self.assertTrue(lam.variables[1].type_ == lambdas.Any)

    def test_reset_data(self):
        self.execute("test(a: Integer, b: String);")
        lam = self.execute("test := (1, 'sf')"
                           "     |  (4, 'fs')"
                           "     ;")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 1)
        lam = self.execute("test := (1, 'sf')"
                           "     |  (2, 'sfs')"
                           "     |  (4, 'fs')"
                           "     ;")
        df = DataFrame(data={'a': [1, 2, 4],
                             'b': ['sf', 'sfs', 'fs']},
                       columns=['a', 'b'])[['a', 'b']]
        self.assertTrue(len(lam.revisions) == 1)
        self.assertTrue(lam.revisions[0].query == hash_df(df))

    def test_appending_data(self):
        self.execute("test(a: Integer, b: String);")
        lam = self.execute("test := (1, 'sf')"
                           "     |  (4, 'fs')"
                           "     ;")
        self.assertTrue(lam is not None)
        self.assertTrue(len(lam.revisions) == 1)
        lam = self.execute("test |= (1, 'sf')"
                           "     |  (2, 'sfs')"
                           "     |  (4, 'fs')"
                           "     ;")
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(len(lam.data) == 3)
        self.assertTrue(all(lam.data['a'] == [1, 4, 2]))

    def test_add_variables(self):
        self.execute("test(a: Integer, b: String);")
        lam = self.execute("test &= (c: String, d: Integer);")
        self.assertTrue(lam.get_type('c') == lambdas.String)
        self.assertTrue(lam.get_type('d') == lambdas.Integer)
        self.assertTrue(len(lam.revisions) == 1)

    def test_add_modify_variables(self):
        self.execute("test(a: Integer, b: String);")
        lam = self.execute("test &= (a: String, d: Integer);")
        self.assertTrue(lam.get_type('a') == lambdas.String)
        self.assertTrue(lam.get_type('d') == lambdas.Integer)
        self.assertTrue(len(lam.revisions) == 2)
        self.assertTrue(isinstance(lam.revisions[0], AddVariableRevision))
        self.assertTrue(isinstance(lam.revisions[1], RetypeVariableRevision))

    def test_retype_variables(self):
        self.execute("test(a: Integer, b: String);")
        lam = self.execute("test &= (a: String);")
        self.assertTrue(lam.get_type('a') == lambdas.String)
        self.assertTrue(len(lam.revisions) == 1)
        self.assertTrue(isinstance(lam.revisions[0], RetypeVariableRevision))

    def test_rename_variables(self):
        self.execute("test(a: Integer, b: String);")
        self.execute("test |= (1, 'a')"
                     "     |  (2, 'b')"
                     "     ;")
        lam = self.execute("test &= (a -> b, b -> a);")
        self.assertTrue(lam.get_type('a') == lambdas.String)
        self.assertTrue(lam.get_type('b') == lambdas.Integer)
        self.assertTrue(isinstance(lam.revisions[1], RenameVariableRevision))
        self.assertTrue(str(lam.data.b.dtype) == 'int64')
        self.assertTrue(str(lam.data.a.dtype) == 'object')
        lam.rollback()
        self.assertTrue(lam.current_revision == 0)
        self.assertTrue(lam.get_type('a') == lambdas.Integer)
        self.assertTrue(lam.get_type('b') == lambdas.String)
        self.assertTrue(str(lam.data.a.dtype) == 'int64')
        self.assertTrue(str(lam.data.b.dtype) == 'object')

    def test_repeat_implementation(self):
        script = """
            student(id: String, name: String, department_name: String, total_credits: Float) 
            := {{ 
                import sqlite3
                import pandas as pd            
                conn = 'sqlite:///data/college_2.sqlite'
                result = pd.read_sql('SELECT * FROM student;', conn)
                result = result.rename(columns={'ID': 'id', 'name': 'name', 'dept_name': 'department_name', 
                                                'tot_cred': 'total_credits'})
                result
               }};        
        """
        lam = self.execute(script)
        self.assertTrue(lam is not None)
        script = """
            student(stuid: Float, last_name: String, first_name: String, age: Float, sex: String, major: Float, 
                    advisor: Float, city_code: String) 
            := {{
                import sqlite3
                import pandas as pd
                conn = 'sqlite:///data/allergy_1.sqlite'
                result = pd.read_sql('SELECT * FROM Student;', conn)
                result = result.rename(columns={'StuID': 'stuid', 'LName': 'last_name', 'Fname': 'first_name', 
                                                'Age': 'age', 'Sex': 'sex', 'Major': 'major', 'Advisor': 'advisor', 
                                                'city_code': 'city_code'})
                result
               }};
        """
        lam2 = self.execute(script)
        self.assertTrue(lam2 is not lam)

    def test_anonymous_implementation(self):
        script = """
            student(id: String, name: String, department_name: String, total_credits: Float) 
            := {{ 
                import sqlite3
                import pandas as pd            
                conn = 'sqlite:///data/college_2.sqlite'
                result = pd.read_sql('SELECT * FROM student;', conn)
                result = result.rename(columns={'ID': 'id', 'name': 'name', 'dept_name': 'department_name', 
                                                'tot_cred': 'total_credits'})
                result
               }};        
        """
        lam = self.execute(script)
        self.assertTrue(lam is not None)
        script = """
            tmp := student(id?, name?, department_name?, total_credits>10?);
        """
        lam2 = self.execute(script)
        self.assertTrue(lam2 is not lam)
        self.assertTrue('id' in lam2.data.columns)
        self.assertTrue('name' in lam2.data.columns)
        self.assertTrue('department_name' in lam2.data.columns)
        self.assertTrue('total_credits' in lam2.data.columns)

    def test_anonymous_implementation_all_cols(self):
        script = """
            student(id: String, name: String, department_name: String, total_credits: Float) 
            := {{ 
                import sqlite3
                import pandas as pd            
                conn = 'sqlite:///data/college_2.sqlite'
                result = pd.read_sql('SELECT * FROM student;', conn)
                result = result.rename(columns={'ID': 'id', 'name': 'name', 'dept_name': 'department_name', 
                                                'tot_cred': 'total_credits'})
                result
               }};        
        """
        lam = self.execute(script)
        self.assertTrue(lam is not None)
        script = """
            tmp := student?;
        """
        lam2 = self.execute(script)
        self.assertTrue(lam2 is not lam)
        self.assertTrue('id' in lam2.data.columns)
        self.assertTrue('name' in lam2.data.columns)
        self.assertTrue('department_name' in lam2.data.columns)
        self.assertTrue('total_credits' in lam2.data.columns)