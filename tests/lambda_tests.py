"""Unit tests for Norm"""
import os

from tests.utils import NormTestCase
from norm.models import Lambda, Variable, Status, Level, lambdas


class LambdaTestCase(NormTestCase):

    def test_exists(self):
        lam1 = Lambda(namespace=self.executor.context_namespace,
                      name='Test',
                      description='Comment 1',
                      variables=[Variable.create(Lambda.VAR_OUTPUT, lambdas.String)])
        self.session.add(lam1)
        self.assertTrue(Lambda.exists(self.session, lam1))
        lam2 = Lambda(namespace=self.executor.context_namespace,
                      name='Test',
                      description='Comment 2',
                      variables=[Variable.create(Lambda.VAR_OUTPUT, lambdas.String)])
        self.assertTrue(not Lambda.exists(self.session, lam2))
        lam3 = Lambda(namespace=self.executor.context_namespace,
                      name='Test',
                      description='Comment 2',
                      variables=[Variable.create(Lambda.VAR_OUTPUT, lambdas.Type)])
        self.assertTrue(not Lambda.exists(self.session, lam3))

    def test_creation(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda',
                     variables=[Variable.create('a', lambdas.String),
                                Variable.create('b', lambdas.Integer),
                                Variable.create('c', lambdas.Datetime)]
                     )
        self.assertTrue(lam is not None)
        self.assertTrue(lam.version.startswith('$'))
        self.assertTrue(lam.status == Status.DRAFT)
        self.assertTrue(lam.ttype == 'float32')
        self.assertTrue(len(lam.variables) == 3)
        self.assertTrue(all([v.type_ is not None for v in lam.variables]))
        self.assertTrue(lam.anchor)
        self.assertTrue(lam.shape == [100])
        self.assertTrue(lam.dtype == 'object')

    def test_clone(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda',
                     variables=[Variable.create('a', lambdas.String),
                                Variable.create('b', lambdas.Integer),
                                Variable.create('c', lambdas.Datetime)]
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
        lam.level = Level.QUERYABLE
        self.assertTrue(lam.folder == 'data/norm/tmp/{}/Test/{}'.format(self.executor.context_id, lam.version))
        lam._create_folder()
        self.assertTrue(os.path.exists(lam.folder))

    def test_empty_data(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda',
                     variables=[Variable.create('a', lambdas.String),
                                Variable.create('b', lambdas.Integer),
                                Variable.create('c', lambdas.Datetime)]
                     )
        lam.level = Level.QUERYABLE
        df = lam.empty_data()
        self.assertTrue(all(df.columns == [lam.VAR_OID, lam.VAR_PROB, lam.VAR_LABEL,
                                           lam.VAR_TIMESTAMP, lam.VAR_TOMBSTONE]
                            + lam._tensor_columns + ['a', 'b', 'c']))
        self.assertTrue(df.dtypes[lam.VAR_TOMBSTONE] == lam.VAR_TOMBSTONE_T)
        self.assertTrue(df.dtypes[lam.VAR_TIMESTAMP] == lam.VAR_TIMESTAMP_T)
        self.assertTrue(df.dtypes[lam.VAR_LABEL] == lam.VAR_LABEL_T)
        self.assertTrue(df.dtypes[lam.VAR_PROB] == lam.VAR_PROB_T)
        self.assertTrue(df.dtypes[lam.VAR_OID] == lam.VAR_OID_T)
        self.assertTrue(all([df.dtypes[col] == lam.ttype for col in lam._tensor_columns]))
        self.assertTrue(df.dtypes['a'] == 'object')
        self.assertTrue(df.dtypes['b'] == 'int')
        self.assertTrue(df.dtypes['c'] == 'datetime64[ns]')

    def test_empty_data_native(self):
        lam = lambdas.String
        self.assertTrue(lam.empty_data() is None)
