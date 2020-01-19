import logging
import traceback
import datetime

from sqlalchemy.exc import SQLAlchemyError
from functools import lru_cache

from norm.compiler import NormCompiler
from norm.models.norm import Module
from norm.executable import Results
from norm.config import Session, MAX_MODULE_CACHE_SIZE
from norm.utils import random_name, new_version

logger = logging.getLogger(__name__)


@lru_cache(MAX_MODULE_CACHE_SIZE)
def build_compiler(module):
    """
    :param module: the module for the compiler
    :type module: Module
    :return: the compiler
    :rtype: NormCompiler
    """
    return NormCompiler(module)


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
    :rtype: Results
    """
    if script is None or not isinstance(script, str):
        return None

    # establish a db session
    session = Session()
    try:
        # retrieve or create a module
        if name and version:
            module = session.query(Module).filter(Module.full_name == name,
                                                  Module.version == version).scalar()
            if module:
                module.script += f'\n# + {datetime.datetime.utcnow()} \n{script}'
            else:
                module = Module(name, script, version=version)
                session.add(module)
        else:
            name = name or random_name()
            version = version or new_version()
            module = Module(name, script, version=version)
            session.add(module)

        compiler = build_compiler(module)\
            .set_python_context(python_context)\
            .set_session(session)

        exes = compiler.compile(script)
        results = [exe.compute() for exe in exes]
        session.commit()
        return results
    except SQLAlchemyError as e:
        logger.error('Object registration failed')
        logger.error(e)
        logger.debug(traceback.print_exc())
        session.rollback()
    finally:
        # close the current db session
        Session.remove()

