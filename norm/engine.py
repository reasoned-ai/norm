import logging
import traceback

from sqlalchemy.exc import SQLAlchemyError
from norm.root import db
from norm.compiler import build_compiler, ParseError, CompileError
from norm.executable import EngineError
from norm.models import ModelError
from norm.utils import random_name

logger = logging.getLogger(__name__)


def execute(script, name=None, python_context=None):
    """
    Execute the script with the module name/version and preset python context.
    :param script: the script to compile
    :type script: str
    :param name: the name of the module
    :type name: str
    :param python_context: the python context
    :type python_context: dict
    :return: the results to return
    :rtype: norm.models.variable.Variable or None
    """
    if script is None or not isinstance(script, str):
        return None

    # establish a db session
    session = db.session
    try:
        name = name or random_name()
        compiler = build_compiler(name)\
            .set_python_context(python_context)\
            .set_session(session)
        exe = compiler.compile(script)
        results = exe.execute()
        session.commit()
        return results
    except ModelError as e:
        logger.error('Norm model failed')
        logger.error(e)
        logger.debug(traceback.print_exc())
        session.rollback()
    except ParseError as e:
        logger.error('Norm parsing failed')
        logger.error(e)
        logger.debug(traceback.print_exc())
        session.rollback()
    except CompileError as e:
        logger.error('Norm compilation failed')
        logger.error(e)
        logger.debug(traceback.print_exc())
        session.rollback()
    except EngineError as e:
        logger.error('Norm execution failed')
        logger.error(e)
        logger.debug(traceback.print_exc())
        session.rollback()
    except SQLAlchemyError:
        logger.error('Norm db operation failed; Try it again.')
        logger.debug(traceback.print_exc())
        session.rollback()

