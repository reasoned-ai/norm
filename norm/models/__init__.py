from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base

import traceback
import logging
logger = logging.getLogger(__name__)

Model = declarative_base()

SEPARATOR = '.'


class ModelError(ValueError):
    pass


class Registrable(object):

    def exists(self):
        """
        Query conditions to check whether the instance already exists or not
        :return: the list of conditions
        :rtype: List
        """
        return NotImplementedError


class Register(object):
    types = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, cls):
        if issubclass(cls, Registrable):
            self.types.append((cls, self.args, self.kwargs))
        else:
            raise ValueError(f"{cls.__name__} is not Registrable")
        return cls

    @classmethod
    def register(cls, overwrite=False):
        from norm.config import Session
        session = Session()
        for clz, args, kwargs in cls.types:
            instance = clz(*args, **kwargs)
            in_store = session.query(clz).filter(*instance.exists()).scalar()
            if not in_store:
                logger.info(f'Registering object {instance.name}: {clz.__name__}')
                session.add(instance)
            elif overwrite:
                instance.id = in_store.id
                logger.info(f'Overwriting object {instance.name}: {clz.__name__}')
                session.merge(instance)
        try:
            session.commit()
        except SQLAlchemyError as e:
            logger.error('Object registration failed')
            logger.error(e)
            logger.debug(traceback.print_exc())
            session.rollback()
        finally:
            Session.remove()


class Store(object):
    def __init__(self, path=''):
        self._items = {}
        self._current_path = path

    def __dir__(self):
        return list(self._items.keys())

    def __getattr__(self, item):
        """
        :type item: str
        :rtype: Store or Model
        """
        if item.startswith('_') or item.find(SEPARATOR) >= 0:
            return None

        if self.current_path:
            p = SEPARATOR.join([self._current_path, item])
        else:
            p = item

        s = self._items.get(p)
        if s is not None:
            return s

        s = Store(p)
        self._items[p] = s
        return s

    @property
    def latest(self):
        # Retrieve the item according to the path, always the latest version
        return None

    def version(self, ver):
        # Retrieve the item according to the path with the given version
        return None


norma = Store()


