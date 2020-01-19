import errno
import logging
import os

logger = logging.getLogger(__name__)


class Storage(object):
    """
    Interface for storing data and model
    """
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


class LocalFile(Storage):

    def _create_folder(self):
        """
        Create the folder for the namespace.
        """
        try:
            # for the case of concurrent processing
            os.makedirs(self.folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                msg = 'Can not create the folder {}'.format(self.folder)
                logger.error(msg)
                logger.error(str(e))
                raise e

    def data_path(self, lam):
        pass

    def model_path(self, lam):
        pass

    def load(self, lam):
        pass

    def save(self, lam):
        pass

