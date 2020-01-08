import norm.config as config
from norm.models.mixins import AuditableMixin
from norm.models.license import License
from norm.models import Model
from norm.models.storage import Storage
from norm.utils import uuid_int

from sqlalchemy import Column, Integer, ForeignKey, Text, exists
from sqlalchemy.orm import relationship, backref
from typing import List

import logging
logger = logging.getLogger(__name__)

metadata = Model.metadata


class Module(Model, AuditableMixin):
    """Module is a Norm script"""
    __tablename__ = 'modules'

    MODULE_SEPARATOR = '.'

    full_name = Column(Text, default='')
    storage_id = Column(Integer, ForeignKey(Storage.id))
    store = relationship(Storage, foreign_keys=[storage_id])
    parent_id = Column(Integer, ForeignKey('modules.id'))
    children = relationship("Module", backref=backref('parent', remote_side=[id]))
    lambdas = relationship("Lambda", back_populates="module")
    license_id = Column(Integer, ForeignKey(License.id))
    license = relationship(License, foreign_keys=[license_id])
    script = Column(Text)

    def __init__(self, full_name, store=None, script=''):
        self.id: int = uuid_int()
        self.script: str = script
        self.name: str = full_name.split(self.MODULE_SEPARATOR)[-1]
        self.full_name: str = full_name
        self.store: Storage = store
        self.sub_modules: List[Module] = []
        self.lambdas: list = []


MODULES = [
    'norm.native',
    'norm.core',
]


def register_modules():
    for mod in MODULES:
        in_store = config.session.query(exists().where(Module.full_name == mod)).scalar()
        if not in_store:
            inst = Module(mod)
            config.session.add(inst)
    config.session.commit()
