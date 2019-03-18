from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base

from norm.config import session, Session

import traceback

import logging
logger = logging.getLogger(__name__)

Model = declarative_base()


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
            if hasattr(clz, 'exists'):
                instance = clz(*args, **kwargs)
                in_store = clz.exists(session, instance)
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
    def restore_lambdas(cls):
        lams = {}
        for clz, args, kwargs in cls.types:
            instance = clz(*args, **kwargs)
            if isinstance(instance, Lambda):
                lam = retrieve_type(instance.namespace, instance.name)
                if lam is not None:
                    if lams.get(lam.name) is not None:
                        msg = '{} has been declared in {}\n'.format(lam.name, lams.get(lam.name))
                        msg += 'now is replaced by {}.{}'.format(lam.namespace, lam.name)
                        logger.warning(msg)
                    lams[lam.name] = lam
        return lams


class Store(object):

    def __init__(self):
        self.items = Register.restore_lambdas()

    def __dir__(self):
        return list(self.items.keys())

    def __getitem__(self, item):
        lam = self.items.get(item, None)
        if lam is not None:
            lam = session.merge(lam)
        return lam

    def __getattr__(self, item):
        lam = self.items.get(item, None)
        if lam is not None:
            lam = session.merge(lam)
        return lam


@event.listens_for(Session, "after_commit")
def save_lambda_after_commit(sess):
    for obj in sess.identity_map.values():
        if isinstance(obj, Lambda) and obj.modified_or_new and obj.status == Status.DRAFT:
            obj.save()


from norm.models.norm import (Variable, lambda_variable, Lambda, GroupLambda, Status, Level, retrieve_type)
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

lambdas = Store()


