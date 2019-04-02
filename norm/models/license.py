"""A collection of ORM sqlalchemy models for managing copyright"""
from norm import config
from norm.models import Model

from sqlalchemy import Column, Integer, String, exists


class License(Model):
    """License for sharing Lambdas"""
    __tablename__ = 'licenses'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)


LICENSES = [
    'MIT',
    'Apache-2.0',
    'CC-0',
    'BSD'
]


def register_licenses():
    for lic in LICENSES:
        in_store = config.session.query(exists().where(License.name == lic)).scalar()
        if not in_store:
            inst = License(name=lic)
            config.session.add(inst)
    config.session.commit()

