from sqlalchemy import Column, String, exists

import norm.config as config
from norm.models import Model
from norm.models.mixins import AuditableMixin


class Storage(Model, AuditableMixin):
    """
    Interface for storing data and model
    """
    __tablename__ = 'storages'
    category = Column(String(128))

    root = Column(String(256), default='')

    __mapper_args__ = {
        'polymorphic_identity': 'storage',
        'polymorphic_on': category,
        'with_polymorphic': '*'
    }

    def __init__(self, name, description, root):
        self.name = name
        self.description = description
        self.root = root

    def data_path(self, lam):
        """
        The absolute path of the data for the lambda
        :param lam: the lambda
        :type lam: norm.models.norm.Lambda
        :return: the path string
        :rtype: str
        """
        raise NotImplementedError

    def model_path(self, lam):
        """
        The absolute path of the model parameters for the lambda
        :param lam: the lambda
        :type lam: norm.models.norm.Lambda
        :return: the path string
        :rtype: str
        """
        raise NotImplementedError

    def _create_folder(self):
        """
        Create the folder for the namespace.
        """
        # TODO: abstract the data storage folder creation
        try:
            # for the case of concurrent processing
            os.makedirs(self.folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                msg = 'Can not create the folder {}'.format(self.folder)
                logger.error(msg)
                logger.error(str(e))
                raise e

    def load(self, lam):
        """
        Load data for the lambda
        :param lam: the lambda
        :type lam: norm.models.norm.Lambda
        :rtype: bool
        """
        raise NotImplementedError

    def save(self, lam):
        """
        Save data for the lambda
        :param lam: the lambda
        :type lam: norm.models.norm.Lambda
        :rtype: bool
        """
        raise NotImplementedError


STORAGES = [
    ('local', 'Local file system', '.norm'),
    ('hdf',   'HDFS system', 'norm'),
    ('gcs',   'Google Cloud Storage', 'norm'),
    ('s3',    'AWS S3 storage', 'norm'),
    ('adl',   'Azure datalake', 'norm')
]


def register_storages():
    for name, description, root in STORAGES:
        in_store = config.session.query(exists().where(Storage.name == name)).scalar()
        if not in_store:
            inst = Storage(name, description, root)
            config.session.add(inst)
    config.session.commit()
