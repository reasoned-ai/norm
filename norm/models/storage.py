import errno
import logging
import os
from datetime import datetime
from typing import Tuple

from pandas import DataFrame
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy import String

from norm.models import Model, Registrable, Register, SEPARATOR
from norm.utils import uuid_int32

logger = logging.getLogger(__name__)


class Storage(Model, Registrable):
    """
    Persistent layer to data and model
    """

    __tablename__ = 'storages'

    category = Column(String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'storage',
        'polymorphic_on': category,
        'with_polymorphic': '*'
    }

    id = Column(Integer, primary_key=True, default=uuid_int32)
    name = Column(String(32), nullable=False, unique=True)
    protocol = Column(String(16), default='file')
    root = Column(String(256), default='')
    created_on = Column(DateTime, default=datetime.utcnow)

    def exists(self):
        return [Storage.name == self.name,
                Storage.root == self.root]

    def copy(self, from_obj: "Registrable"):
        pass

    def path(self, module):
        """
        :param module: the module
        :type module: norm.models.norm.Module
        :return: the absolute path of the module
        :rtype: str
        """
        raise NotImplementedError

    def load(self, lam):
        """
        Load data for the lambda
        :param lam: the lambda
        :type lam: norm.models.norm.Lambda
        :return: data and function
        :rtype: Tuple[DataFrame, Callable]
        """
        raise NotImplementedError

    def save(self, lam, data, func):
        """
        Save data for the lambda
        :param lam: the lambda
        :type lam: norm.models.norm.Lambda
        :param data: the data for the lambda
        :type data: DataFrame
        :param func: the callable func for the lambda
        :type func: Callable
        :rtype: bool
        """
        raise NotImplementedError


@Register(name='unix_user_default', root='~/.norm')
class UnixFile(Storage):

    __mapper_args__ = {
        'polymorphic_identity': 'storage_unix_file',
    }

    def __init__(self, name, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = 'file'
        self.name = name
        self.root = root

    @staticmethod
    def _create_folder(folder):
        """
        Create the folder for the namespace.
        """
        try:
            # for the case of concurrent processing
            os.makedirs(folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                msg = f'Can not create the folder {folder}'
                logger.error(msg)
                logger.error(str(e))
                raise e

    def path(self, module):
        return f"{self.protocol}://{os.path.expanduser(self.root)}/{module.name.replace(SEPARATOR, '/')}/"
