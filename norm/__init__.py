from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool

from IPython import get_ipython
from IPython.core.magic import register_line_magic, register_cell_magic, register_line_cell_magic

import os
import logging
logger = logging.getLogger(__name__)

context = None


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
    from norm.config import Session
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
        Session.configure(bind=config.engine)
        config.session = Session()
        config.context_id = str(datetime.utcnow().strftime('%m%d%Y.%H%M%S'))
        global context
        from norm.security import user
        from norm.engine import NormCompiler, NormError
        context = NormCompiler(config.context_id, user, config.session)


def init_jupyter():
    from norm.engine import NormCompiler, NormError
    from norm.config import session, context_id
    from norm.security import user, login
    logging.disable()
    global context
    user = login()
    context = NormCompiler(context_id, user, session)


def init_colab():
    """
    Setting the configurations in Colab (Google)
    """
    # Login the user
    from google.colab import auth
    from google.colab import drive
    auth.authenticate_user()
    import requests
    from gcloud import credentials
    logging.basicConfig(level=logging.DEBUG)
    access_token = credentials.get_credentials().get_access_token().access_token
    gcloud_tokeninfo = requests.get('https://www.googleapis.com/oauth2/v3/userinfo?access_token=' + access_token).json()
    email = gcloud_tokeninfo['email']
    last_name = gcloud_tokeninfo['hd']
    first_name = email.split('@')[0]

    # Mount the drive
    drive.mount('/content/drive')

    # Configure the database
    home = '/content/drive/My Drive/.norm/'
    if not os.path.exists(home):
        os.mkdir(home)
        logging.info("Directory " + home + " created ")
    else:
        logging.info("Directory " + home + " already exists")

    from norm.config import Session
    from norm import config, security

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
    Session.configure(bind=config.engine)
    config.session = Session()
    config.context_id = str(datetime.utcnow().strftime('%m%d%Y.%H%M%S'))

    from norm.security import login
    user = login({'first_name': first_name,
                  'last_name': last_name,
                  'username': email,
                  'email': email})

    logging.info(user.username + ' logged in')

    global context
    from norm.engine import NormCompiler, NormError
    context = NormCompiler(config.context_id, user, config.session)


# IPython magics
if get_ipython() is not None:
    def update_python_context():
        context.python_context = ip.user_global_ns

    def try_norma(lines):
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].rstrip(' \t\r\n') != '':
                lines = lines[:(i+1)]
                break
        if lines[-1].rstrip(' \t\r\n')[-1] == ';':
            context.python_context = ip.user_global_ns
            return ['%%norma\n'] + lines
        else:
            return lines
    ip = get_ipython()
    ip.input_transformers_cleanup.append(try_norma)

    @register_line_cell_magic
    def norma(line, cell=None):
        """
        Parsing the norm command and execute it
        :param line: a line of norm command
        :type line: str
        :param cell: a multi-line of norm command
        :type cell: str
        """
        from norm.engine import NormCompiler, NormError
        import norm.config as config
        try:
            if cell is None:
                result = context.execute(line)
            else:
                result = context.execute(cell)

            config.session.commit()
            return result
        except SQLAlchemyError as e:
            config.session.rollback()
            msg = 'Session commit failed on {}'.format(config.engine)
            logger.error(msg)
            logger.error(e)
            raise NormError(msg)
