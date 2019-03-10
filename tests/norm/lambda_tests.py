"""Unit tests for Norm"""
import os

from tests.norm.utils import NormTestCase
from norm.models import Lambda, Variable, retrieve_type, Status, Level


class LambdaTestCase(NormTestCase):

    def test_creation(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda',
                     variables=[Variable('a', retrieve_type('norm.native', 'String', session=self.session)),
                                Variable('b', retrieve_type('norm.native', 'Integer', session=self.session)),
                                Variable('c', retrieve_type('norm.native', 'Datetime', session=self.session))]
                     )
        self.assertTrue(lam is not None)
        self.assertTrue(lam.version is None)
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
                     variables=[Variable('a', retrieve_type('norm.native', 'String', session=self.session)),
                                Variable('b', retrieve_type('norm.native', 'Integer', session=self.session)),
                                Variable('c', retrieve_type('norm.native', 'Datetime', session=self.session))]
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
        self.assertTrue(lam.signature == '{}.Test@None'.format(self.executor.context_namespace))
        lam = Lambda(namespace=None, name='Test')
        self.assertTrue(lam.signature == 'Test@None')
        lam = Lambda(name='Test')
        lam.version = 23
        self.assertTrue(lam.signature == 'Test@23')

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
        self.assertTrue(lam.folder == 'data/norm/tmp/testing/Test')
        lam._create_folder()
        self.assertTrue(os.path.exists(lam.folder))

    def test_empty_data(self):
        lam = Lambda(namespace=self.executor.context_namespace,
                     name='Test',
                     description='Test lambda',
                     variables=[Variable('a', retrieve_type('norm.native', 'String', session=self.session)),
                                Variable('b', retrieve_type('norm.native', 'Integer', session=self.session)),
                                Variable('c', retrieve_type('norm.native', 'Datetime', session=self.session))]
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
        lam = retrieve_type('norm.native', 'String', session=self.session)
        self.assertTrue(lam.empty_data() is None)
