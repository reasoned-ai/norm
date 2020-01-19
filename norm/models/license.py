"""A collection of ORM sqlalchemy models for managing copyright"""
from norm.utils import uuid_int
from norm.models import Model, Registrable, Register

from sqlalchemy import Column, Integer, String


@Register(name='MIT')
@Register(name='BSD')
@Register(name='Apache', version='2.0')
@Register(name='CC', version='0')
class License(Model, Registrable):
    """License for sharing Lambdas"""
    __tablename__ = 'licenses'

    id = Column(Integer, primary_key=True, default=uuid_int)
    name = Column(String(32), nullable=False)
    full_name = Column(String(256))
    version = Column(String(32))

    def __init__(self, name, version=None, full_name=None):
        self.id = uuid_int()
        self.name = name
        self.full_name = full_name
        self.version = version

    def __repr__(self):
        if self.full_name:
            return self.full_name
        if self.version:
            return f"{self.name}-{self.version}"
        return self.name

    def __str__(self):
        return self.__repr__()

    def exists(self):
        return [License.name == self.name,
                License.version == self.version]

