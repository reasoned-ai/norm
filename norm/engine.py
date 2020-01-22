import logging
import traceback

from sqlalchemy.exc import SQLAlchemyError

from norm.compiler import build_compiler, ParseError, CompileError
from norm.config import Session
from norm.executable import Results, NormError
from norm.utils import random_name, new_version

logger = logging.getLogger(__name__)


def execute(script, name=None, version=None, python_context=None):
    """
    Execute the script with the module name/version and preset python context.
    :param script: the script to compile
    :type script: str
    :param name: the name of the module
    :type name: str
    :param version: the version of the module
    :type version: str
    :param python_context: the python context
    :type python_context: dict
    :return: the results to return
    :rtype: Results or None
    """
    if script is None or not isinstance(script, str):
        return None

    # establish a db session
    session = Session()
    try:
        name = name or random_name()
        version = version or new_version()
        compiler = build_compiler(name, version)\
            .set_python_context(python_context)\
            .set_session(session)

        results = None
        for exe in compiler.compile(script):
            results = exe.compute()

        session.commit()
        return results
    except (ParseError, CompileError):
        logger.error('Norm parsing or compilation failed')
        logger.debug(traceback.print_exc())
        session.rollback()
    except NormError:
        logger.error('Norm execution failed')
        logger.debug(traceback.print_exc())
        session.rollback()
    except SQLAlchemyError:
        logger.error('Norm db operation failed; Try it again.')
        logger.debug(traceback.print_exc())
        session.rollback()
    finally:
        # close the current db session
        Session.remove()

