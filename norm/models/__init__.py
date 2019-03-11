import traceback

from sqlalchemy import exists
from sqlalchemy.ext.declarative import declarative_base
Model = declarative_base()

from norm.config import session
import logging
logger = logging.getLogger(__name__)


class Register(object):
    types = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, cls):
        self.types.append((cls, self.args, self.kwargs))
        return cls

    @classmethod
    def register(cls):
        for clz, args, kwargs in cls.types:
            instance = clz(*args, **kwargs)
            in_store = session.query(exists().where(clz.name == instance.name)).scalar()
            if not in_store:
                logger.info('Registering class {}'.format(instance.name))
                session.add(instance)
        try:
            session.commit()
        except:
            logger.error('Type registration failed')
            logger.debug(traceback.print_exc())
            session.rollback()
            session.close()

    @classmethod
    def retrieve(cls, clz, *args, **kwargs):
        instance = clz(*args, **kwargs)
        stored_inst = session.query(clz).filter(clz.name == instance.name).scalar()
        if stored_inst is None:
            stored_inst = instance
            session.add(instance)
        return stored_inst


from norm.models.norm import (Variable, lambda_variable, Lambda, Status, Level,
                              KerasLambda, retrieve_type)
from norm.models.revision import (Revision, revision_variable, SchemaRevision, AddVariableRevision,
                                  DeleteVariableRevision, RenameVariableRevision, RetypeVariableRevision,
                                  DeltaRevision, ConjunctionRevision, DisjunctionRevision, FitRevision)
from norm.models.python import PythonLambda
from norm.models.native import (NativeLambda, TypeLambda, AnyLambda, ListLambda,
                                BooleanLambda, IntegerLambda, StringLambda,
                                PatternLambda, UUIDLambda, FloatLambda,
                                URLLambda, DatetimeLambda, TensorLambda)
from norm.models.core import (CoreLambda, StringFormatterLambda, ExtractPatternLambda, ReadFileLambda)
from norm.models.license import License

