import unittest
import hashids
import time
import os

hashid = hashids.Hashids()

__all__ = ['user_tester', 'NormTestCase']

os.environ['NORM_DATA_STORAGE_ROOT'] = 'data'
os.environ['NORM_DB_PATH'] = 'norm/db/norm.db'

from norm.config import session


def user_tester():
    from norm.models.user import User
    tester = session.query(User).filter(User.username == 'tester',
                                        User.email == 'norm-tester@reasoned.ai').first()
    if tester is None:
        tester = User(username='tester', first_name='tester', last_name='norm',
                      email='norm-tester@reasoned.ai')
        session.add(tester)
        session.commit()
    return tester


class NormTestCase(unittest.TestCase):

    def setUp(self):
        from norm.engine import NormEngine
        self.session = session
        # override norm configuration
        self.user = user_tester()
        self.context_id = hashid.encode(int(time.time() * 1000))
        self.executor = NormEngine(self.context_id, self.user, self.session)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def execute(self, script):
        return self.executor.execute(script)
