from collections import OrderedDict

from pandas import DataFrame, Series

from norm.executable import NormError
from norm.executable.constant import ListConstant, Constant
from norm.executable.expression import NormExpression
from norm.executable.expression.condition import ConditionExpr, CombinedConditionExpr
from norm.executable.expression.evaluation import AddDataEvaluationExpr, DataFrameColumnFunctionExpr
from norm.grammar.literals import LOP

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

    def __combine_value(self, value1, value2):
        if value1 is None or value2 is None:
            return None
        elif isinstance(value1, ListConstant) and isinstance(value2, ListConstant):
            value1.value.extend(value2.value)
            return value1
        elif isinstance(value1, ListConstant) and isinstance(value2, Constant):
            value1.value.append(value2.value)
            return value1
        elif isinstance(value1, Constant) and isinstance(value2, ListConstant):
            value2.value.append(value1.value)
            return value2
        elif isinstance(value1, Constant) and isinstance(value2, Constant):
            return ListConstant(value1.type_, [value1.value, value2.value])
        elif isinstance(value1, AddDataEvaluationExpr) and isinstance(value2, AddDataEvaluationExpr):
            # pushdown the combine operation
            if value1.lam is value2.lam:
                combined = self.__combine_data(value1.data, value2.data)
                if combined is not None:
                    value1.data = combined
                    return value1
        return None

    def __combine_data(self, data1, data2):
        cols = list(data1.keys())
        cols.extend(col for col in data2.keys() if col not in data1.keys())
        data = OrderedDict()
        for col in cols:
            combined = self.__combine_value(data1.get(col), data2.get(col))
            if combined is None:
                return None
            else:
                data[col] = combined
        return data

    def compile(self, context):
        if isinstance(self.expr1, AddDataEvaluationExpr) and isinstance(self.expr2, AddDataEvaluationExpr)\
                and self.expr1.lam is self.expr2.lam:
            # Combine the constant arguments for adding data
            # ensure that all arguments are constants
            combined = self.__combine_data(self.expr1.data, self.expr2.data)
            if combined is not None:
                self.expr1.data = combined
                return self.expr1
        if isinstance(self.expr1, ConditionExpr) and isinstance(self.expr2, ConditionExpr):
            return CombinedConditionExpr(self.op, self.expr1, self.expr2).compile(context)

        self.lam = context.temp_lambda(self.expr1.lam.variables +
                                       [v for v in self.expr2.lam.variables if v.name not in self.expr1.lam])
        return self

    def execute(self, context):
        df1 = self.expr1.execute(context)
        if isinstance(df1, Series):
            df1 = DataFrame(data={df1.name: df1})
        df2 = self.expr2.execute(context)
        if isinstance(df2, Series):
            df2 = DataFrame(data={df2.name: df2})

        # TODO: OR to union
        from norm.models.norm import Lambda
        if self.op == LOP.AND:
            # both indices are the same, left join to df2
            # if not, cross join df1 and df2
            if df1.index.name == df2.index.name:
                cols = [col for col in df1.columns if col not in df2.columns]
                df2[cols] = df1.loc[df2.index, cols]
            else:
                df1['__join__'] = 1
                df2['__join__'] = 1
                if df1.index.name is not None:
                    df1 = df1.reset_index()
                df1.set_index('__join__')
                if df2.index.name is not None:
                    df2 = df2.reset_index()
                df2.set_index('__join__')
                cols = [col for col in df1.columns if col not in df2.columns]
                df2 = df2.join(df1[cols]).reset_index(drop=True)

        if df2.index.name != Lambda.VAR_OID and df2.index.name is not None:
            df2 = df2.reset_index()
        return df2


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

    def execute(self, context):
        msg = 'Negated query is not executable, but only compilable'
        logger.error(msg)
        raise NormError(msg)

