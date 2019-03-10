"""A collection of ORM sqlalchemy models for managing copyright"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from norm import config

from sqlalchemy import Column, Integer, String, exists

Model = config.Model


class License(Model):
    """License for sharing Lambdas"""
    __tablename__ = 'licenses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)


LICENSES = [
    'Apache-2.0',
    'MIT',
    'CC-0',
    'BSD'
]


def register_licenses():
    for lic in LICENSES:
        in_store = config.db.session.query(exists().where(License.name == lic)).scalar()
        if not in_store:
            inst = License(name=lic)
            config.db.session.add(inst)
    config.db.session.commit()

