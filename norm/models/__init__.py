import sys

from sqlalchemy import func, desc
from sqlalchemy.orm import with_polymorphic
from sqlalchemy.orm.exc import MultipleResultsFound

from norm.root import db
from norm.grammar import SEPARATOR, VERSION_SIGN
from sqlalchemy.exc import SQLAlchemyError

from typing import TYPE_CHECKING, Optional, List, Dict, Type, Tuple, Any, cast

if TYPE_CHECKING:
    from norm.models.norm import Lambda, Module, Variable, PythonLambda
    from norm.models.storage import Storage

import traceback
import logging

logger = logging.getLogger(__name__)

Model = db.Model


class ModelError(ValueError):
    pass


class Registrable(object):

    def __init__(self, *args, **kwargs):
        self.name: str = ''

    def copy(self, from_obj: "Registrable"):
        """
        Copy the out-of-db states
        :param from_obj: copy from another object
        """
        raise NotImplementedError

    def exists(self) -> List:
        """
        Query conditions to check whether the instance already exists or not
        :return: the list of conditions
        """
        raise NotImplementedError


class Register(object):
    types: List[Tuple[Type[Registrable], Tuple[Any, ...], Dict[str, Any]]] = []

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
            try:
                in_store = session.query(clz).filter(*instance.exists()).scalar()
                if not in_store:
                    logger.info(f'Registering object {instance.name}: {clz.__name__}')
                    session.add(instance)
                elif overwrite:
                    instance.id = in_store.id
                    logger.info(f'Overwriting object {instance.name}: {clz.__name__}')
                    session.merge(instance)
            except MultipleResultsFound as e:
                logger.error(f'Multiple result for {instance}')
                logger.error(e)
                logger.debug(traceback.print_exc())
                session.rollback()
                return
        try:
            session.commit()
        except SQLAlchemyError as e:
            logger.error('Object registration failed')
            logger.error(e)
            logger.debug(traceback.print_exc())
            session.rollback()


class Store(object):
    def __init__(self, path=''):
        # TODO: make it lru_cache
        self._items: Dict[str, Registrable] = {}
        self._current_path = path

    def __retrieve(self, item: str) -> Optional[Registrable]:
        """
        Retrieve item from cache
        :param item:
        :return:
        """
        obj = self._items.get(item)
        if obj is not None:
            merged_obj: Registrable = db.session.merge(obj)
            merged_obj.copy(obj)
            return merged_obj
        return None

    def __getitem__(self, signature: str) -> Optional[Registrable]:
        """
        Get registrable object by signature
        :param signature: the object signature
        :return: the object
        """
        if signature is None:
            return None

        signature = signature.strip()
        if signature == '':
            return None

        obj = self.__retrieve(signature)
        if obj is not None:
            return obj

        items = signature.split(SEPARATOR)
        if items[0] == 'storage':
            obj = self._get_storage(SEPARATOR.join(items[1:]))
        elif len(items) == 1:
            obj = self._get_module(items[0])
        else:
            name = SEPARATOR.join(items[0:-1])
            module = self.__retrieve(name)
            if module is None:
                module = self._get_module(name)
            names = items[-1].split(VERSION_SIGN)
            if len(names) == 1:
                version = None
            elif len(names) == 2:
                version = names[1]
            else:
                raise ModelError(f"More than one $ is found in the qualified name {items[-1]}")
            obj = self._get_lambda(names[0], module, version)

        if obj is None:
            return None

        self._items[signature] = obj
        return obj

    def fetch_lambda(self, module_names: List[str], name: str, version: str = None) -> Optional["Lambda"]:
        from norm.models.norm import Lambda, Module
        for module_name in module_names:
            signature: str = SEPARATOR.join([module_name, name])
            if version is not None:
                signature = VERSION_SIGN.join([signature, version])
            obj: Lambda = cast(Lambda, self.__retrieve(signature))
            if obj is not None:
                return obj

            module: Module = cast(Module, self.__retrieve(module_name))
            if module is None:
                module = self._get_module(module_name)
            obj = self._get_lambda(name, module, version)

            if obj is None:
                continue

            self._items[signature] = obj
            return obj

        return None

    @staticmethod
    def _get_storage(name: str) -> Optional["Storage"]:
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
            store = self._get_storage('unix_user_default')
        module = Module(name, description, store)
        db.session.add(module)
        self._items[name] = module
        db.session.commit()
        return module

    @staticmethod
    def _get_module(name: str) -> Optional["Module"]:
        """
        Get module by the name
        :param name: the name of the module
        :return: the module
        """
        if not name:
            return None

        from norm.models.norm import Module
        import norm.models.native
        import norm.models.core
        q = db.session.query(with_polymorphic(Module, '*'))
        q = q.filter(func.lower(Module.name) == func.lower(name))
        return q.scalar()

    @staticmethod
    def _get_lambda(name: str, module: "Module", version: str = None) -> Optional["Lambda"]:
        """
        Get Lambda by fully qualified name
        :param name: the name with optional version
        :param module: the module for the lambda
        :param version: the version of the lambda
        :return: the lambda
        """
        if not name:
            return None

        from norm.models.norm import Lambda, Module
        from norm.models import native, core

        q = db.session.query(with_polymorphic(Lambda, '*'))

        conds = [func.lower(Lambda.name) == func.lower(name),
                 Lambda.module_id == module.id]
        if version is not None:
            conds.append(Lambda.version == version)
            lam = q.filter(*conds).scalar()
        else:
            lam = q.filter(*conds).order_by(desc(Lambda.created_on))
            lam = lam.first()

        return lam

    def create_lambda(self, name: str, module: "Module", version: str = None, description: str = '',
                      atomic: bool = False, bindings: List["Variable"] = None) -> Optional["Lambda"]:
        """
        Create a lambda
        :param name: the name
        :param module: the module, default to current module
        :param version: the version, default to None
        :param description: the description for the lambda
        :param atomic: whether it contains subsets or not
        :param bindings: a list of variables involved in the lambda
        :return: the lambda
        """
        assert (module is not None)
        from norm.models.norm import Lambda
        lam = Lambda(module=module,
                     name=name,
                     description=description,
                     version=version,
                     atomic=atomic,
                     bindings=bindings)
        db.session.add(lam)
        key_latest = f'{module.name}{SEPARATOR}{name}'
        self._items[key_latest] = lam
        key_versioned = f'{module.name}{SEPARATOR}{name}${lam.version}'
        self._items[key_versioned] = lam
        return lam

    @staticmethod
    def create_python_lambda(name: str, module: "Module", version: str = None, description: str = '',
                             python_version: str = sys.version, atomic: bool = False,
                             bindings: List["Variable"] = None) -> Optional["PythonLambda"]:
        from norm.models.norm import PythonLambda
        lam = PythonLambda(name=name, description=description, module=module, version=version,
                           python_version=python_version, atomic=atomic, bindings=bindings)
        db.session.add(lam)
        return lam


norma = Store()
