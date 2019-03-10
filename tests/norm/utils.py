from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import superset

from norm.config import db, user_model
from norm.engine import executor
from norm.utils import set_current_user
import unittest

__all__ = ['superset', 'user_tester', 'NormTestCase']


def user_tester():
    tester = db.session.query(user_model).filter(user_model.username == 'tester',
                                                 user_model.email == 'norm-tester@reasoned.ai').first()
    if tester is None:
        tester = user_model(username='tester', first_name='tester', last_name='norm',
                            email='norm-tester@reasoned.ai', password='')
        db.session.add(tester)
        db.session.commit()

    set_current_user(tester)
    return tester


class NormTestCase(unittest.TestCase):

    def setUp(self):
        self.session = db.session
        self.user = user_tester()
        self.context_id = 'testing'
        self.executor = executor(self.context_id, self.session)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def execute(self, script):
        return self.executor.execute(script)
