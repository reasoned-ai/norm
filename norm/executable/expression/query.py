from norm.executable import ListConstant, NormError
from norm.executable.expression import NormExpression, Projection
from norm.executable.expression.argument import ArgumentExpr
from norm.executable.expression.condition import ConditionExpr, CombinedConditionExpr
from norm.executable.expression.evaluation import EvaluationExpr
from norm.literals import LOP

import logging
logger = logging.getLogger(__name__)


class QueryExpr(NormExpression):

    def __init__(self, op, expr1, expr2):
        """
        Query expression
        :param op: logical operation, e.g., [&, |, ^, =>, <=>]
        :type op: LOP
        :param expr1: left expression
        :type expr1: NormExpression
        :param expr2: right expression
        :type expr2: NormExpression
        """
        super().__init__()
        self.op = op
        self.expr1 = expr1
        self.expr2 = expr2

    @staticmethod
    def __pad_arguments(args, length, fill_value=None):
        """
        Pad the argument values with fill_value
        :param args: the list of argument values
        :type args: List
        :param length: the length of the argument to fill
        :type length: int
        :param fill_value: the fill value
        :type fill_value: Any
        :return: the filled list
        :rtype: List
        """
        if len(args) >= length:
            return args
        elif len(args) < length:
            return args + [fill_value] * (length - len(args))

    def compile(self, context):
        if isinstance(self.expr1, EvaluationExpr) and self.expr1.is_to_add_data()\
                and isinstance(self.expr2, EvaluationExpr) and self.expr2.is_to_add_data():
            # Combine the constant arguments for adding data
            # ensure that all arguments are constants
            if self.expr1.is_constant_arguments and self.expr2.is_constant_arguments:
                # Assuming the first constant type is respected, if the following types are different,
                #     they will be converted
                # If two arguments are of different length, the missing values will be filled with N/A
                length = max(len(self.expr1.args), len(self.expr2.args))
                args = [ArgumentExpr(None, None, ListConstant(arg1.expr.type_, [arg1.expr.value, arg2.expr.value]))
                        for arg1, arg2 in zip(self.__pad_arguments(self.expr1.args, length),
                                              self.__pad_arguments(self.expr2.args, length))]
                return EvaluationExpr(args)
            else:
                # TODO: combine expressions instead of just constants
                pass
        if isinstance(self.expr1, ConditionExpr) and isinstance(self.expr2, ConditionExpr):
            return CombinedConditionExpr(self.op, self.expr1, self.expr2)
        return self

    def serialize(self):
        pass

    def execute(self, context):
        lam1 = self.expr1.execute(context)
        lam2 = self.expr2.execute(context)
        # TODO: AND to intersect, OR to union
        return lam2


class NegatedQueryExpr(NormExpression):

    def __init__(self, expr):
        """
        Negation of the expression
        :param expr: the expression to negate
        :type expr: NormExpression
        """
        super().__init__()
        self.expr = expr

    def compile(self, context):
        if isinstance(self.expr, QueryExpr):
            self.expr.expr1 = NegatedQueryExpr(self.expr.expr1).compile(context)
            self.expr.expr2 = NegatedQueryExpr(self.expr.expr2).compile(context)
            self.expr.op = self.expr.op.negate()
        elif isinstance(self.expr, ConditionExpr):
            self.expr.op = self.expr.op.negate()
        else:
            msg = 'Currently NOT only works on logically combined query or conditional query'
            logger.error(msg)
            raise NotImplementedError(msg)
        return self.expr

    def serialize(self):
        pass

    def execute(self, context):
        msg = 'Negated query is not executable, but only compilable'
        logger.error(msg)
        raise NormError(msg)

