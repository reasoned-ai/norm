from typing import Union

from norm.executable import NormError
from norm.executable.constant import Constant
from norm.grammar.literals import COP, ConstantType, LOP

from norm.executable.expression import NormExpression
from norm.executable.schema.variable import VariableName

import logging
logger = logging.getLogger(__name__)


class ConditionExpr(NormExpression):

    def __init__(self, op, lexpr, rexpr):
        """
        Condition expression
        :param op: conditional operation, e.g., [<, <=, >, >=, =, !=, in, !in, ~]. ~ means 'like'
        :type op: Union[COP, LOP]
        :param lexpr: arithmetic expression, e.g., a + b - c
        :type lexpr: Union[ArithmeticExpr, ConditionExpr]
        :param rexpr: another arithmetic expression
        :type rexpr: Union[ArithmeticExpr, ConditionExpr]
        """
        super().__init__()
        from norm.executable.expression.arithmetic import ArithmeticExpr
        self.op: COP = op
        self.lexpr: Union[ArithmeticExpr, ConditionExpr] = lexpr
        self.rexpr: Union[ArithmeticExpr, ConditionExpr] = rexpr
        self._condition = None
        assert(self.lexpr is not None)
        assert(self.rexpr is not None)
        assert(self.op is not None)

    def __str__(self):
        if self._condition is None:
            msg = 'Compile the condition expression first'
            logger.error(msg)
            raise NormError(msg)
        return self._condition

    def compile(self, context):
        if self.op == COP.LK:
            assert(isinstance(self.lexpr, VariableName))
            assert(isinstance(self.rexpr, Constant))
            assert(self.rexpr.type_ is ConstantType.STR or self.rexpr.type_ is ConstantType.PTN)
            self._condition = '{}.str.contains({})'.format(self.lexpr, self.rexpr)
        else:
            self._condition = '({}) {} ({})'.format(self.lexpr, self.op, self.rexpr)
        self.eval_lam = self.lexpr.lam
        self.lam = context.temp_lambda(self.eval_lam.variables)
        self.lam.cloned_from = self.eval_lam
        return self

    def execute(self, context):
        self.lexpr.execute(context)
        self.lam.data = self.eval_lam.data.query(self._condition, engine='python')
        return self.lam.data


class CombinedConditionExpr(ConditionExpr):

    def __init__(self, op, lexpr, rexpr):
        """
        Combined conditional expression
        :param op: logical operation, e.g., ['and', 'or'] others are not supported yet # TODO support xor, imp, eqv
        :type op: LOP
        :param lexpr: left conditional expression
        :type lexpr: ConditionExpr
        :param rexpr:right conditional expression
        :type rexpr: ConditionExpr
        """
        super().__init__(op, lexpr, rexpr)

    def compile(self, context):
        if self._condition is not None:
            return self

        self.lexpr = self.lexpr.compile(context)
        self.rexpr = self.rexpr.compile(context)
        self._condition = '({}) {} ({})'.format(self.lexpr, self.op, self.rexpr)
        assert(self.lexpr.eval_lam is self.rexpr.eval_lam or self.lexpr.eval_lam is self.rexpr.eval_lam.cloned_from)
        self.eval_lam = self.lexpr.eval_lam
        self.lam = context.temp_lambda(self.eval_lam.variables)
        self.lam.cloned_from = self.eval_lam
        return self

    def execute(self, context):
        self.lam.data = self.eval_lam.data.query(self._condition, engine='python')
        return self.lam.data
