from norm.models.norm import retrieve_type, Status
from norm.executable import NormExecutable

from typing import Union

import logging
logger = logging.getLogger(__name__)


class VariableName(NormExecutable):

    def __init__(self, scope, name):
        """
        The variable and its scope
        :param scope: the scope of the variable
        :type scope: Union[VariableName, norm.executable.expression.evaluation.EvaluationExpr] or None
        :param name: the name of the variable
        :type name: str
        """
        super().__init__()

        self.scope = scope  # type: VariableName
        self.name = name  # type: str
        from norm.models.norm import Lambda
        self.lam = None  # type: Lambda

    def __str__(self):
        if self.scope is not None:
            return '{}.{}'.format(self.scope, self.name)
        else:
            return self.name

    def variable_type(self):
        return self.lam

    def compile(self, context):
        session = context.session

        if self.scope is None:
            name = self.name
            if context.scope and name in context.scope:
                return ColumnVariable(None, name).compile(context)
            else:
                lam = retrieve_type(context.context_namespace, name, session=session)
                if lam is None:
                    lam = retrieve_type(context.search_namespaces, name, status=Status.READY, session=session)
                self.lam = lam
                return self
        else:
            if isinstance(self.scope, ColumnVariable) and self.scope.name + '.' + self.name in self.scope.lam:
                # Already joined
                self.scope.name += '.' + self.name
                return self.scope

            lam = self.scope.variable_type()
            if self.name in lam:
                if isinstance(self.scope, (ColumnVariable, JoinVariable)):
                    # Join lam to the scope for the column
                    return JoinVariable(self.scope, self.name, lam).compile(context)
                else:
                    # A column of the scope variable
                    return ColumnVariable(self.scope, self.name).compile(context)
            else:
                # An evaluation whose first argument is the scope
                lam = retrieve_type(context.context_namespace, self.name, session=session)
                if lam is None:
                    lam = retrieve_type(context.search_namespaces, self.name, status=Status.READY,
                                        session=session)
                assert(lam is not None)
                self.lam = lam
                from norm.executable.expression.argument import ArgumentExpr
                arg = ArgumentExpr(None, None, self.scope, None)
                self.scope = None
                from norm.executable.expression.evaluation import EvaluationExpr
                return EvaluationExpr([arg], self)

    def execute(self, context):
        return self.lam


class ColumnVariable(VariableName):

    def __init__(self, scope, name):
        super().__init__(scope, name)

    def variable_type(self):
        return self.lam.get_type(self.name)

    def compile(self, context):
        if self.scope is None:
            assert(context.scope is not None)
            self.lam = context.scope
        else:
            self.lam = self.scope.lam
        return self

    def execute(self, context):
        lam = self.scope.execute(context).clone()
        from norm.models.norm import Variable
        lam.variables = [Variable(str(self), self.variable_type())]
        return lam


class JoinVariable(VariableName):

    def __init__(self, scope, name, joiner):
        super().__init__(scope, name)
        from norm.models.norm import Lambda
        self.lam = joiner  # type: Lambda

    def variable_type(self):
        return self.lam.get_type(self.name)

    def compile(self, context):
        return self

    def execute(self, context):
        lam = self.scope.execute(context).clone()
        from norm.models.norm import Variable
        lam.variables.append(Variable(str(self), self.variable_type()))
        lam.df = lam.data.join(self.lam.data[[self.name]].rename(columns={self.name: str(self)}), on=str(self.scope))
        return lam
