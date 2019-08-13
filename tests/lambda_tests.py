"""Unit tests for Norm"""
import os

from tests.utils import NormTestCase
from norm.models import Lambda, Variable, Status, lambdas


class LambdaTestCase(NormTestCase):

    def test_exists(self):
        lam1 = Lambda(namespace=self.executor.context_namespace,
                      name='Test',
                      description='Comment 1',
                      variables=[Variable(Lambda.VAR_OUTPUT, lambdas.String)])
        self.session.add(lam1)
        self.assertTrue(Lambda.exists(self.session, lam1))
        lam2 = Lambda(namespace=self.executor.context_namespace,
                      name='Test',
                      description='Comment 2',
                      variables=[Variable(Lambda.VAR_OUTPUT, lambdas.String)])
        self.assertTrue(not Lambda.exists(self.session, lam2))
        lam3 = Lambda(namespace=self.executor.context_namespace,
                      name='Test',
                      description='Comment 2',
                      variables=[Variable(Lambda.VAR_OUTPUT, lambdas.Type)])
        self.assertTrue(not Lambda.exists(self.session, lam3))

    def test_creation(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda',
                     variables=[Variable('a', lambdas.String),
                                Variable('b', lambdas.Integer),
                                Variable('c', lambdas.Datetime)]
                     )
        self.assertTrue(lam is not None)
        self.assertTrue(lam.version.startswith('$'))
        self.assertTrue(lam.status == Status.DRAFT)
        self.assertTrue(len(lam.variables) == 3)
        self.assertTrue(all([v.type_ is not None for v in lam.variables]))
        self.assertTrue(lam.anchor)
        self.assertTrue(lam.dtype == 'object')

    def test_clone(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda',
                     variables=[Variable('a', lambdas.String),
                                Variable('b', lambdas.Integer),
                                Variable('c', lambdas.Datetime)]
                     )
        lam.status = Status.READY
        cloned = lam.clone()
        self.assertTrue(cloned.cloned_from is lam)
        self.assertFalse(cloned.anchor)
        self.assertTrue(cloned.status == Status.DRAFT)

    def test_signature(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda'
                     )
        self.assertTrue(lam.signature.startswith('{}.Test$'.format(self.executor.context_namespace)))
        lam = Lambda(namespace=None, name='Test')
        self.assertTrue(lam.signature.startswith('Test$'))
        lam = Lambda(name='Test')
        lam.version = '$23'
        self.assertTrue(lam.signature == 'Test$23')

    def test_check_draft_status(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda'
                     )
        lam.status = Status.READY
        with self.assertRaises(RuntimeError):
            lam.rollback()

    def test_create_folder(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda'
                     )
        lam.queryable = True
        self.assertTrue(lam.folder == 'data/norm/tmp/{}/Test/{}'.format(self.executor.context_id, lam.version))
        lam._create_folder()
        self.assertTrue(os.path.exists(lam.folder))

    def test_empty_data(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda',
                     variables=[Variable('a', lambdas.String),
                                Variable('b', lambdas.Integer),
                                Variable('c', lambdas.Datetime)]
                     )
        lam.queryable = True
        df = lam.empty_data()
        self.assertTrue(all(df.columns == [lam.VAR_PROB, lam.VAR_LABEL, lam.VAR_TIMESTAMP, lam.VAR_TOMBSTONE] +
                            ['a', 'b', 'c']))
        self.assertTrue(df.dtypes[lam.VAR_TOMBSTONE] == lam.VAR_TOMBSTONE_T)
        self.assertTrue(df.dtypes[lam.VAR_TIMESTAMP] == lam.VAR_TIMESTAMP_T)
        self.assertTrue(df.dtypes[lam.VAR_LABEL] == lam.VAR_LABEL_T)
        self.assertTrue(df.dtypes[lam.VAR_PROB] == lam.VAR_PROB_T)
        self.assertTrue(df.dtypes['a'] == 'object')
        self.assertTrue(df.dtypes['b'] == 'int')
        self.assertTrue(df.dtypes['c'] == 'datetime64[ns]')

    def test_empty_data_native(self):
        lam = lambdas.String
        self.assertTrue(lam.empty_data() is None)

    def test_save_data(self):
        script = """
            player(player_id: String, birth_year: Float, birth_month: Float, birth_day: Float, birth_country: String, 
                   birth_state: String, birth_city: String, death_year: Float, death_month: Float, death_day: Float, 
                   death_country: String, death_state: String, death_city: String, name_first: String, 
                   name_last: String, name_given: String, weight: Float, height: Float, bats: String, 
                   throws: String, debut: String, final_game: String, retro_id: String, bbref_id: String) 
            := {{
                from sqlalchemy import create_engine
                import sqlite3
                import pandas as pd
                engine = create_engine('sqlite:///data/baseball_1.sqlite')
                conn = engine.raw_connection()
                def try_str(a):
                    try:
                        return a.decode('utf-8')
                    except:
                        return 'not utf-8'
                conn.connection.text_factory = try_str    
                result = pd.read_sql('SELECT * FROM player;', conn)
                result = result.rename(columns={'player_id': 'player_id', 'birth_year': 'birth_year', 
                                                'birth_month': 'birth_month', 'birth_day': 'birth_day', 
                                                'birth_country': 'birth_country', 'birth_state': 'birth_state', 
                                                'birth_city': 'birth_city', 'death_year': 'death_year', 
                                                'death_month': 'death_month', 'death_day': 'death_day', 
                                                'death_country': 'death_country', 'death_state': 'death_state', 
                                                'death_city': 'death_city', 'name_first': 'name_first', 
                                                'name_last': 'name_last', 'name_given': 'name_given', 
                                                'weight': 'weight', 'height': 'height', 'bats': 'bats', 
                                                'throws': 'throws', 'debut': 'debut', 'final_game': 'final_game', 
                                                'retro_id': 'retro_id', 'bbref_id': 'bbref_id'})
                result
               }};        
        """
        lam = self.execute(script)
        lam = self.execute("export player test.spider.baseball_1;")
        self.assertTrue(os.path.exists(lam.folder))
        for revision in lam.revisions:
            self.assertTrue(os.path.exists(revision.path))
