from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool

from norm.engine import NormCompiler, NormError
from norm.config import Session
from norm import config
from norm.security import user

from IPython import get_ipython
from IPython.core.magic import register_line_magic, register_cell_magic, register_line_cell_magic

import os
import logging
logger = logging.getLogger(__name__)

context = NormCompiler(config.context_id, user, config.session)


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
        context = NormCompiler(config.context_id, user, config.session)


# IPython magics
if get_ipython() is not None:
    @register_line_cell_magic
    def norm(line, cell=None):
        """
        Parsing the norm command and execute it
        :param line: a line of norm command
        :type line: str
        :param cell: a multi-line of norm command
        :type cell: str
        """
        try:
            if cell is None:
                if line.strip('\n\t ')[-1] != ';':
                    line += ';'
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
