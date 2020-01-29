"""A collection of ORM sqlalchemy models for CoreLambda"""
import logging

from norm.models import store, Registrable, Register
from norm.models.norm import Lambda, Module

logger = logging.getLogger(__name__)

__version__ = '1'


@Register()
class CoreModule(Module):
    __mapper_args__ = {
        'polymorphic_identity': 'module_core'
    }

    def __init__(self):
        super().__init__('norm.core', description='Norm core namespace', version=__version__)


class CoreLambda(Lambda, Registrable):
    """
    Core functions are at the computable level and predefined in the code base
    """
    __mapper_args__ = {
        'polymorphic_identity': 'lambda_core'
    }

    def __init__(self, name, description, module=None, version=None, atomic=True, bindings=None):
        super().__init__(module=module or store.core.latest,
                         name=name,
                         description=description,
                         version=version or __version__,
                         atomic=atomic,
                         bindings=bindings or [])

    def exists(self):
        return [CoreLambda.name == self.name,
                CoreLambda.version == self.version]

    def empty_data(self):
        return None


