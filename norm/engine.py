import logging
import traceback
from typing import Dict, Optional
from sqlalchemy.exc import SQLAlchemyError
from norm import db
from norm.compiler import build_compiler, ParseError, CompileError
from norm.executable import EngineError
from norm.models import ModelError
from norm.utils import random_name
from norm.config import USE_DASK, DataFrame

logger = logging.getLogger('norm.engine')


def execute(script: str, module_name: str = None, python_context: Dict = None) -> Optional["DataFrame"]:
    """
    Execute the script with the module name/version and preset python context.
    :param script: the script to compile
    :param module_name: the name of the module
    :param python_context: the python context
    :return: a DataFrame
    """
    logger.debug(script)
    if script is None or not isinstance(script, str) or script.strip('') == '':
        return None

    session = db.session
    try:
        module_name = module_name or random_name()
        compiler = build_compiler(module_name)\
            .set_python_context(python_context)\
            .set_session(session)
        exe = compiler.compile(script)
        if exe is None:
            return None
        results = exe.execute()
        if results is None:
            return None
        session.commit()
        return results.data
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
    except SQLAlchemyError as e:
        logger.error('Norm db operation failed; Try it again.')
        logger.error(e)
        logger.debug(traceback.print_exc())
        session.rollback()
    except Exception as e:
        logger.error('Other errors')
        logger.error(e)
        logger.debug(traceback.print_exc())
        session.rollback()

