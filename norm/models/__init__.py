from sqlalchemy import func, desc
from sqlalchemy.orm import with_polymorphic

from norm.root import db
from sqlalchemy.exc import SQLAlchemyError

from typing import TYPE_CHECKING, Optional, Union
if TYPE_CHECKING:
    from norm.models.norm import Lambda, Module
    from norm.models.storage import Storage

import traceback
import logging
logger = logging.getLogger(__name__)

Model = db.Model

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
        session = db.session
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


class Store(object):
    def __init__(self, path=''):
        self._items = {}
        self._current_path = path

    def __getitem__(self, item: str) -> Union["Module", "Lambda", "Storage", type(None)]:
        """
        Get the lambda by name
        :param item: the object name
        :return: the object
        """
        if item is None:
            return None

        item = item.strip()
        if item == '':
            return None

        obj = self._items.get(item)
        if obj is not None:
            return db.session.merge(obj)

        items = item.split(SEPARATOR)
        if items[0] == 'storage':
            obj = self.get_storage(SEPARATOR.join(items[1:]))
        elif len(items) == 1:
            obj = self.get_module(items[0])
        else:
            module = self.get_module(SEPARATOR.join(items[0:-1]))
            obj = self.get_lambda(items[-1], module)

        if obj is None:
            return None

        self._items[item] = obj
        return obj

    @staticmethod
    def get_storage(name: str) -> Optional["Storage"]:
        """
        Get storage by the name
        :param name: the name of the storage
        :return: the storage
        """
        if not name:
            return None

        from norm.models.storage import Storage
        q = db.session.query(with_polymorphic(Storage, '*'))
        return q.filter(func.lower(Storage.name) == func.lower(name)).scalar()

    def create_module(self, name: str, description: str, store: "Storage" = None) -> Optional["Module"]:
        """
        Create module by the name
        :param name: the name of the module
        :param description: the description of the module
        :param store: the storage for the module
        :return: the module
        """
        if not name:
            return None

        from norm.models.norm import Module
        if store is None:
            store = self.get_storage('unix_user_default')
        module = Module(name, description, store)
        db.session.add(module)
        self._items[name] = module
        db.session.commit()
        return module

    @staticmethod
    def get_module(name: str) -> Optional["Module"]:
        """
        Get module by the name
        :param name: the name of the module
        :return: the module
        """
        if not name:
            return None

        from norm.models.norm import Module
        from norm.models.native import NativeModule
        from norm.models.core import CoreModule
        q = db.session.query(Module)
        q = q.filter(func.lower(Module.name) == func.lower(name))
        return q.scalar()

    @staticmethod
    def get_lambda(name: str, module: "Module") -> Optional["Lambda"]:
        """
        Get Lambda by fully qualified name
        :param name: the name with optional version
        :param module: the module for the lambda
        :return: the lambda
        """
        if not name:
            return None

        from norm.models.norm import Lambda, Module
        from norm.models.native import AnyLambda, DatetimeLambda, IntegerLambda, NativeLambda, OperatorLambda,\
            StringLambda, TypeLambda, UUIDLambda, BooleanLambda, FloatLambda
        from norm.models.core import DescribeLambda, CoreLambda, SummaryLambda, RenameLambda, RetypeLambda
        q = db.session.query(with_polymorphic(Lambda, '*'))
        names = name.split('$')
        if len(names) == 1:
            version = 'latest'
        elif len(names) == 2:
            version = names[1]
        else:
            raise ModelError(f"More than one $ is found in the qualified name {name}")

        conds = [func.lower(Lambda.name) == func.lower(names[0]),
                 Lambda.module_id == module.id]
        if version != 'latest':
            conds.append(Lambda.version == version)
            lam = q.filter(*conds).scalar()
        else:
            lam = q.filter(*conds).order_by(desc(Lambda.created_on)).first()

        return lam


norma = Store()


