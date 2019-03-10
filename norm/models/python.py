"""A collection of ORM sqlalchemy models for PythonLambda"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from norm.models.norm import Lambda, Status

import logging
logger = logging.getLogger(__name__)


class PythonLambda(Lambda):

    __mapper_args__ = {
        'polymorphic_identity': 'lambda_python'
    }

    def __init__(self, namespace, name, description, dtype='object'):
        assert(namespace is not None and isinstance(namespace, str))
        assert(namespace.startswith('python'))

        super().__init__(namespace=namespace,
                         name=name,
                         description=description,
                         variables=[],
                         dtype=dtype)
        self.status = Status.READY
        self.shape = []

    def __call__(self, *args, **kwargs):
        """
        TODO: implement
        """
        pass

