import unittest
from norm.config import session

__all__ = ['user_tester', 'NormTestCase']


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
        from norm.engine import NormCompiler
        self.session = session
        self.user = user_tester()
        self.context_id = 'testing'
        self.executor = NormCompiler(self.context_id, self.user, self.session)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def execute(self, script):
        return self.executor.execute(script)
