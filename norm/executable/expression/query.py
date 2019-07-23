from collections import OrderedDict
from typing import List

from pandas import DataFrame, Series, merge, concat

from norm.executable import NormError
from norm.executable.constant import ListConstant, Constant, TupleConstant
from norm.executable.expression import NormExpression
from norm.executable.expression.condition import ConditionExpr, CombinedConditionExpr
from norm.executable.expression.evaluation import AddDataEvaluationExpr, DataFrameColumnFunctionExpr
from norm.grammar.literals import LOP

import logging
logger = logging.getLogger(__name__)

CROSS_JOIN_KEY = '__key__'


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
        elif isinstance(value1, list) and isinstance(value2, list):
            value1.extend(value2)
            return value1
        elif isinstance(value1, list) and not isinstance(value2, list):
            value1.append(value2)
            return value1
        elif not isinstance(value1, list) and isinstance(value2, list):
            value2.append(value1)
            return value2
        elif isinstance(value1, AddDataEvaluationExpr) and isinstance(value2, AddDataEvaluationExpr):
            # pushdown the combine operation
            if value1.lam is value2.lam:
                combined = self.__combine_data(value1.data, value2.data)
                if combined is not None:
                    value1.data = combined
                    return value1
        elif not isinstance(value1, list) and not isinstance(value2, list):
            return [value1, value2]
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
                if len(cols) > 0:
                    df2[cols] = df1.loc[df2.index, cols]
            else:
                df1[CROSS_JOIN_KEY] = 1
                df2[CROSS_JOIN_KEY] = 1
                if df1.index.name is not None:
                    df1 = df1.reset_index()
                if df2.index.name is not None:
                    df2 = df2.reset_index()
                cols = [col for col in df1.columns if col not in df2.columns]
                df2 = merge([df2, df1[cols]]).drop(columns=[CROSS_JOIN_KEY])

        if df2.index.name != Lambda.VAR_OID and df2.index.name is not None:
            df2 = df2.reset_index()
        self.lam.data = df2
        return df2


class ConstantAssignmentExpr(NormExpression):

    def __init__(self, constant, projection=None):
        """
        Assign constant to a variable and join with the current scope
        :param constant: the constant to assign
        :type constant: Constant
        :param projection: the variable to project to
        :type projection: Projection
        """
        super().__init__()
        from norm.executable import Projection
        self.constant: Constant = constant
        self.projection: Projection = projection
        self.variable_name: str = None

    @property
    def var_type(self):
        from norm.models import lambdas
        return lambdas[self.constant.type_.value.title()]

    def compile(self, context):
        assert(self.projection is not None)
        if len(self.projection.variables) > 1:
            return MultipleConstantAssignmentExpr(self.constant, self.projection).compile(context)

        from norm.models.norm import Variable
        self.variable_name = self.projection.variables[0].name
        if context.scope is not None:
            self.eval_lam = context.scope
            variables = self.eval_lam.variables
            self.lam = context.temp_lambda(variables + [Variable(self.variable_name, self.var_type)])
        else:
            self.eval_lam = None
            self.lam = context.temp_lambda([Variable(self.variable_name, self.var_type)])
        return self

    def execute(self, context):
        if not isinstance(self.constant, ListConstant):
            if self.eval_lam is not None:
                df = self.eval_lam.data
                df[self.variable_name] = self.constant.value
            else:
                df = DataFrame(data={self.variable_name: [self.constant.value]})
        else:
            if self.eval_lam is not None:
                df = self.eval_lam.data
                if self.variable_name not in df.columns:
                    df[CROSS_JOIN_KEY] = 1
                    to_join = DataFrame({self.variable_name: self.constant.value})
                    to_join[CROSS_JOIN_KEY] = 1
                    df = df.merge(to_join, on=CROSS_JOIN_KEY, how='outer').drop(columns=[CROSS_JOIN_KEY])
                else:
                    assert(len(df) == len(self.constant.value))
                    df[self.variable_name] = self.constant.value
            else:
                df = DataFrame(data={self.variable_name: self.constant.value})
        self.lam.data = df
        return df


class MultipleConstantAssignmentExpr(NormExpression):

    def __init__(self, constant, projection):
        """
        Assign constant to a variable and join with the current scope
        :param constant: the constant to assign
        :type constant: Constant
        :param projection: the variables to project to
        :type projection: Projection
        """
        super().__init__()
        from norm.executable import Projection
        self.constant: Constant = constant
        self.projection: Projection = projection

    @property
    def var_names(self):
        return [v.name for v in self.projection.variables]

    @property
    def var_types(self):
        from norm.models import lambdas
        return [lambdas[t.value.title()] for t in self.constant.type_]

    def compile(self, context):
        assert(isinstance(self.constant, ListConstant))
        assert(isinstance(self.constant.value[0], tuple))
        assert(len(self.var_names) == len(self.var_types))
        assert(self.eval_lam is None or all(vn not in self.eval_lam for vn in self.var_names))
        from norm.models.norm import Variable
        vs = [Variable(n, t) for n, t in zip(self.var_names, self.var_types)]
        if context.scope is not None:
            self.eval_lam = context.scope
            variables = self.eval_lam.variables
            self.lam = context.temp_lambda(variables + vs)
        else:
            self.eval_lam = None
            self.lam = context.temp_lambda(vs)
        return self

    def execute(self, context):
        if self.eval_lam is not None:
            df = self.eval_lam.data
            if any(vn in df.columns for vn in self.var_names):
                assert(len(df) == len(self.constant.value))
                df[self.var_names] = self.constant.value
            else:
                df[CROSS_JOIN_KEY] = 1
                to_join = DataFrame(data=self.constant.value,
                                    columns=self.var_names)
                to_join[CROSS_JOIN_KEY] = 1
                df = df.merge(to_join, on=CROSS_JOIN_KEY, how='outer').drop(columns=[CROSS_JOIN_KEY])
        else:
            df = DataFrame(data=self.constant.value, columns=self.var_names)
        self.lam.data = df
        return df


class QuantifiedQueryExpr(NormExpression):

    def __init__(self, expr, quantifiers):
        """
        Quantify result by the quantifiers
        :param expr: the expression to query
        :type expr: NormExpression
        :param quantifiers: the list of quantifiers to evaluate
        :type quantifiers: Quantifiers
        """
        super().__init__()
        self.expr = expr
        self.quantifiers = quantifiers

    def compile(self, context):
        self.eval_lam = self.expr.eval_lam
        self.lam = self.expr.lam
        return self

    def execute(self, context):
        df = self.expr.execute(context)
        assert(isinstance(df, DataFrame))
        return self.quantifiers.quantify(df)


class PivotQueryExpr(NormExpression):

    def __init__(self, expr, projection):
        """
        Unquoted projection essentially does the pivoting
        :param expr: the expression to evaluate
        :type expr: NormExpression
        :param projection: the unquoted projection to pivot
        :type projection: Projection
        """
        super().__init__()
        self.expr = expr
        self.projection = projection
        self.cols = []
        self.var_name = None

    def compile(self, context):
        assert(len(self.projection.variables) == 1)
        from norm.executable.schema.variable import UnquoteVariable
        v = self.projection.variables[0]
        assert(isinstance(v, UnquoteVariable))
        self.cols = [uv.name for uv in v.unquoted_variables]
        self.var_name = v.name
        self.lam = self.expr.lam
        self.eval_lam = v.lam
        return self

    def execute(self, context):
        result = self.expr.execute(context)
        # TODO: this is a hack, have to think about which value columns in general are referred to
        col_values = [self.expr.lam.variables[-1].name]
        col_index = [col for col in result.columns if col not in col_values and col not in self.cols]
        if len(col_index) == 0:
            col_index = result.index
        for col in self.cols:
            if col not in result.columns:
                result[col] = self.eval_lam.data[col]
        df = result.pivot_table(values=col_values, columns=self.cols, index=col_index, aggfunc=lambda x: x)
        df.columns = [self.var_name.format(*col_values) for col_values in zip(*df.columns.levels[1:])]
        if col_index is not result.index:
            df = df.reset_index()
        return df


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

