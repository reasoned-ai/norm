from sqlalchemy.ext.declarative import declarative_base

from norm.config import session

import traceback

import logging
logger = logging.getLogger(__name__)

Model = declarative_base()


class Register(object):
    types = []
    types_by_name = {}

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, cls):
        self.types.append((cls, self.args, self.kwargs))
        return cls

    @classmethod
    def register(cls):
        for clz, args, kwargs in cls.types:
            if hasattr(clz, 'exists'):
                instance = clz(*args, **kwargs)
                in_store = clz.exists(session, instance)
                if not in_store:
                    logger.info('Registering class {}'.format(instance.name))
                    session.add(instance)
        try:
            session.commit()
        except:
            logger.error('Type registration failed')
            logger.debug(traceback.print_exc())
            session.rollback()

    @classmethod
    def restore_lambda(cls, item):
        if len(cls.types_by_name) == 0:
            for clz, args, kwargs in cls.types:
                instance = clz(*args, **kwargs)
                cls.types_by_name[instance.name] = instance
        instance = cls.types_by_name.get(item)
        if instance is not None and isinstance(instance, Lambda):
            return retrieve_type(instance.namespace, instance.name)
        else:
            return None


class Store(object):

    def __init__(self):
        self._items = dict()

    def __restore(self, item):
        lam = None
        try:
            lam = Register.restore_lambda(item)
            self._items[item] = lam
        except Exception as e:
            msg = 'Norm store is not ready'
            logger.warning(msg)
            logger.warning(e)
        return lam

    def __dir__(self):
        return list(self._items.keys())

    def is_empty(self):
        return len(self._items) == 0

    def __getitem__(self, item):
        lam = self._items.get(item, None)
        if lam is None:
            # reload in case there are more lambdas just got registered
            lam = self.__restore(item)
            if lam is None:
                msg = 'Can not find {}'.format(item)
                logger.warning(msg)

        if lam is not None:
            lam = session.merge(lam)
        return lam

    def __getattr__(self, item):
        return self.__getitem__(item)


from norm.models.norm import (Variable, Lambda, Status, retrieve_type)
from norm.models.revision import (Revision, revision_variable, SchemaRevision, AddVariableRevision,
                                  DeleteVariableRevision, RenameVariableRevision, RetypeVariableRevision,
                                  DeltaRevision, ConjunctionRevision, DisjunctionRevision, FitRevision)
from norm.models.python import PythonLambda
from norm.models.native import (NativeLambda, TypeLambda, AnyLambda, ListLambda,
                                BooleanLambda, IntegerLambda, StringLambda,
                                PatternLambda, UUIDLambda, FloatLambda,
                                URLLambda, DatetimeLambda)
from norm.models.core import (CoreLambda, StringFormatterLambda, ExtractPatternLambda, ReadFileLambda)
from norm.models.license import License

lambdas = Store()


