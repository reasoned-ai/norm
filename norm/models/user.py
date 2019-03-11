from sqlalchemy import Column, Integer, String, DateTime
from norm.models import Model


class User(Model):
    """
    Partial declaration to be compatible to the server side
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(64), unique=True, nullable=False)
    last_login = Column(DateTime)
    login_count = Column(Integer)
    fail_login_count = Column(Integer)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __repr__(self):
        return self.get_full_name()

    def __str__(self):
        return self.get_full_name()
