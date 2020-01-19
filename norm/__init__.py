import logging
import os

from IPython import get_ipython
from IPython.core.magic import register_line_cell_magic
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from norm.utils import random_name, new_version

logger = logging.getLogger(__name__)


def configure(home=None, db_path=None, data_path=None, **kwargs):
    """
    Setting the parameters for Norm
    :param home: the path to the db and the data, e.g., /home/<user>/.norm
    :type home: str
    :param db_path: the path to the db, e.g., /home/<user>/.norm/db/norm.db
    :type db_path: str
    :param data_path: the path to the data, e.g., /home/<user>/.norm/data
    :type data_path: str
    :param kwargs: other parameters
    """
    from norm import config

    if home is not None:
        config.NORM_HOME = home
        config.DATA_STORAGE_ROOT = os.path.join(home, 'data')
        config.DB_PATH = os.path.join(home, 'db/norm.db')
    if db_path is not None:
        config.DB_PATH = db_path
    if data_path is not None:
        config.DATA_STORAGE_ROOT = data_path
    if home is not None or db_path is not None:
        config.engine = create_engine('sqlite:///{}'.format(config.DB_PATH), poolclass=StaticPool)
        config.Session.configure(bind=config.engine)


def init_colab():
    """
    Setting the configurations in Colab (Google)
    """
    # Login the user
    from google.colab import auth
    from google.colab import drive
    # Authenticate user
    auth.authenticate_user()
    # Mount the drive
    drive.mount('/content/drive')
    # Configure the database
    home = '/content/drive/My Drive/.norm/'
    if not os.path.exists(home):
        os.mkdir(home)
        logging.info("Directory " + home + " created ")
    else:
        logging.info("Directory " + home + " already exists")

    from norm import config

    config.NORM_HOME = home

    config.DATA_STORAGE_ROOT = os.path.join(home, 'data')
    if not os.path.exists(config.DATA_STORAGE_ROOT):
        os.mkdir(config.DATA_STORAGE_ROOT)
        logging.info("Directory " + config.DATA_STORAGE_ROOT + " created ")
    else:
        logging.info("Directory " + config.DATA_STORAGE_ROOT + " already exists")

    db_path = os.path.join(home, 'db')
    if not os.path.exists(db_path):
        os.mkdir(db_path)
        logging.info("Directory " + db_path + " created ")
    else:
        logging.info("Directory " + db_path + " already exists")

    config.DB_PATH = os.path.join(home, 'db/norm.db')
    if not os.path.exists(config.DB_PATH):
        orig_db_file = os.path.join(os.path.dirname(__file__), 'db/norm.db')
        from shutil import copyfile
        copyfile(orig_db_file, config.DB_PATH)
        logging.info("File " + config.DB_PATH + " copied")
    else:
        logging.info("File " + config.DB_PATH + " already exists")

    config.engine = create_engine('sqlite:///{}'.format(config.DB_PATH), poolclass=StaticPool)
    config.Session.configure(bind=config.engine)


# IPython magics
if get_ipython() is not None:
    ip = get_ipython()
    context = {'module_name': random_name(),
               'module_version': new_version()}

    def init_context():
        context.clear()
        context['module_name'] = random_name()
        context['module_version'] = new_version()

    @register_line_cell_magic
    def norma(line, cell=None):
        """
        Parsing the norm command and execute it
        :param line: a line of norm command
        :type line: str
        :param cell: a multi-line of norm command
        :type cell: str
        """
        from norm.engine import execute
        module_name = context.get('module_name')
        module_version = context.get('module_version')
        script = cell or line
        return execute(script, module_name, module_version, ip.user_global_ns)
