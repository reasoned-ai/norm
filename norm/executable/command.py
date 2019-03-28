from norm.executable import NormExecutable
from norm.executable.schema.type import TypeName
from norm.grammar.literals import MOP

import logging
logger = logging.getLogger(__name__)


class Command(NormExecutable):

    def __init__(self, op, type_name):
        """
        The interactive commands.
            * revisions:  show all revisions for the given version or the current version
            * versions: show all historical versions for the given version or all
            * redo: re-apply the next revision
            * undo: roll-back the current revision
        :param op: the operation of the command
        :type op: MOP
        :param type_name: the lambda
        :type type_name: TypeName
        """
        super().__init__()
        self.op = op
        self.type_name = type_name
        self.lam = None

    def compile(self, context):
        session = context.session
        return self

    def execute(self, context):
        # TODO
        return None
