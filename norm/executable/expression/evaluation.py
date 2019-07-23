import uuid
from enum import Enum

from norm.utils import hash_df
from pandas import DataFrame, Series, Index

from norm.grammar.literals import COP
from norm.executable import NormError, Projection
from norm.executable.expression.argument import ArgumentExpr
from norm.executable.schema.variable import VariableName, ColumnVariable, JoinVariable
from norm.executable.expression import NormExpression

from collections import OrderedDict

from typing import List, Dict

import logging
logger = logging.getLogger(__name__)


class EvaluationExpr(NormExpression):

    def __init__(self, args, variable=None, projection=None):
        """
        The evaluation of an expression either led by a variable name
        :param args: the arguments provided
        :type args: List[ArgumentExpr]
        :param variable: the variable name to evaluate
        :type variable: VariableName
        :type projection: Projection
        """
        super().__init__()
        self.variable: VariableName = variable
        self.args: List[ArgumentExpr] = args
        self.inputs: Dict[str, DataFrame] = None
        self.outputs: Dict[str, str] = None
        self.join_variables: List[JoinVariable] = []
        self.projection: Projection = projection
        self.equalities: Dict[str, str] = None
        from norm.models.norm import Lambda
        self.equality_scope: Lambda = None

    @property
    def is_constant_arguments(self):
        return all(arg.is_constant for arg in self.args)

    def check_assignment_arguments(self):
        """
        Check whether the arguments are in the style of assignments. Ex. 234, 'asfs', b=3, c=5
        :return: True or False
        :rtype: bool
        """
        keyword_arg = False  # positional argument
        for arg in self.args:
            if arg.op is None:
                if arg.variable is None:
                    if keyword_arg:
                        msg = 'Keyword based arguments should come after positional arguments'
                        logger.error(msg)
                        logger.error([str(arg) for arg in self.args])
                        raise NormError(msg)
                else:
                    keyword_arg = True
            else:
                return False
        return True

    def build_assignment_inputs(self, lam):
        """
        If the arguments are in assignment style, build the inputs as assignments
        :param lam: given the Lambda to be evaluated
        :return: a dictionary mapping from a variable to an expression for the inputs
        :rtype: Dict
        """
        if lam.nargs == 0:
            # Lambda is anonymously created
            from norm.models.norm import Lambda
            return OrderedDict((arg.variable.name if arg.variable else '{}{}'.format(Lambda.VAR_ANONYMOUS_STUB, i),
                                arg.expr) for i, arg in enumerate(self.args))

        keyword_arg = False
        inputs = OrderedDict()
        from norm.models.norm import Variable
        for ov, arg in zip(lam.variables, self.args):  # type: Variable, ArgumentExpr
            if arg.expr is None:
                continue

            if arg.op is None and arg.variable is not None:
                keyword_arg = True
            if not keyword_arg:
                inputs[ov.name] = arg.expr
            else:
                inputs[arg.variable.name] = arg.expr
        return inputs

    def build_conditional_inputs(self):
        """
        If the arguments are in conditional style, build the inputs as conditionals
        :return: a query string
        :rtype: Dict
        """
        self.equalities = OrderedDict()
        self.equality_scope = None
        inputs = []
        for arg in self.args:
            if (arg.is_assign_operator or arg.op is COP.EQ) and isinstance(arg.expr, ColumnVariable) and \
                    isinstance(arg.variable, ColumnVariable):
                self.equalities[arg.expr.name] = arg.variable.name
                if self.equality_scope is None:
                    self.equality_scope = arg.expr.lam
                else:
                    assert(self.equality_scope is arg.expr.lam)
                continue
            if arg.op is None or arg.expr is None:
                continue
            vn = arg.variable.name
            if isinstance(arg.variable, JoinVariable):
                self.join_variables.append(arg.variable)
                vn = str(arg.variable)
            if arg.op == COP.LK:
                condition = '{}.str.contains({})'.format(vn, arg.expr)
            else:
                condition = '{} {} ({})'.format(vn, arg.op, arg.expr)
            inputs.append(condition)
        return ' and '.join(inputs)

    def build_outputs(self, lam):
        """
        Build the outputs according to the projection
        :return: a dictionary mapping from the original variable to the new variable
        :rtype: Dict
        """
        from norm.models.norm import Lambda
        assert(isinstance(lam, Lambda))
        outputs = OrderedDict()
        from norm.models.norm import Variable
        for ov, arg in zip(lam.variables, self.args):  # type: Variable, ArgumentExpr
            if arg.projection is not None:
                assert(len(arg.projection.variables) <= 1)
                if arg.variable is None:
                    outputs[ov.name] = arg.projection.variables[0].name
                else:
                    if len(arg.projection.variables) == 0:
                        outputs[arg.variable.name] = arg.variable.name
                    else:
                        outputs[arg.variable.name] = arg.projection.variables[0].name
        if self.projection is not None:
            assert(len(self.projection.variables) <= 1)
            if self.projection.num == 1:
                new_lambda_name = self.projection.variables[0].name
            else:
                new_lambda_name = lam.name
            outputs = OrderedDict((key, self.VARIABLE_SEPARATOR.join([new_lambda_name, value])) for key, value
                                  in outputs.items())
            if lam.is_functional:
                outputs[lam.VAR_OUTPUT] = new_lambda_name
            else:
                outputs[lam.VAR_OID] = new_lambda_name
        return outputs

    def compile(self, context):
        if self.variable is None:
            from norm.models.norm import Lambda
            assert(context.scope is not None)
            assert(isinstance(context.scope, Lambda))
            lam = context.scope
            # constructing new objects
            assert(self.check_assignment_arguments())
            self.inputs = self.build_assignment_inputs(lam)
            self.outputs = None
            is_to_add_data = True
        else:
            lam = self.variable.lam
            if lam is None:
                # Might need to be combined with previous context
                return self
            if self.check_assignment_arguments():
                self.inputs = self.build_assignment_inputs(lam)
                is_to_add_data = not lam.atomic
            else:
                self.inputs = self.build_conditional_inputs()
                is_to_add_data = False
            self.outputs = self.build_outputs(lam)
            is_to_add_data &= len(self.outputs) == 0

        if self.equality_scope is not None and len(self.equalities) > 0:
            return JoinEqualityEvaluationExpr(lam, self.equality_scope, self.equalities, self.inputs, self.outputs)\
                .compile(context)

        if is_to_add_data:
            return AddDataEvaluationExpr(lam, self.inputs, self.variable is not None).compile(context)
        elif isinstance(self.inputs, dict):
            if self.projection is not None and self.projection.num == 1:
                output_projection = self.projection.variables[0].name
            else:
                output_projection = None
            if lam.atomic:
                return AtomicEvaluationExpr(lam, self.inputs, output_projection).compile(context)
            elif len(self.inputs) == 0:
                if isinstance(self.variable, ColumnVariable):
                    return ArgumentExpr(self.variable, None, None, self.projection).compile(context)
                elif self.projection is not None and len(self.outputs) == 1:
                    return RetrieveAllDataExpr(lam, output_projection).compile(context)
                else:
                    return RetrievePartialDataExpr(lam, self.outputs).compile(context)
        self.eval_lam = lam
        from norm.models import Variable
        if len(self.outputs) > 0:
            variables = [Variable(self.outputs[v.name], v.type_) for v in self.eval_lam.variables
                         if v.name in self.outputs.keys()]
        else:
            variables = self.eval_lam.variables
        self.lam = context.temp_lambda(variables)
        self.lam.cloned_from = self.eval_lam
        return self

    def execute(self, context):
        for jv in self.join_variables:
            jv.execute(context)
        df = self.eval_lam.data.query(self.inputs, engine='python')

        if isinstance(df, DataFrame) and len(self.outputs) > 0:
            df = df[self.outputs.keys()].rename(columns=self.outputs)
        self.lam.data = df
        return df


class JoinEqualityEvaluationExpr(NormExpression):

    def __init__(self, lam, scope, equalities, condition, outputs):
        """
        Join the input scope first and then evaluate
        Event(name?, ip?eip) & Cluster(ip=eip, name~'App'?cluster_name);
        :param lam: the current scope
        :param scope: the input scope
        :param equalities: the equalities, e.g., {'eip':'ip'}
        :param condition: the other condition, e.g., 'name.str.contains("App")'
        :param outputs: the outputs for the current scope, e.g., {'name':'cluster_name'}
        """
        super().__init__()
        self.eval_lam = lam
        self.scope = scope
        self.equalities = equalities
        self.condition = condition
        self.outputs = outputs

    def compile(self, context):
        scope = self.scope
        from norm.models import Lambda, Variable
        if len(self.outputs) > 0:
            variables = [Variable(v.name, v.type_) for v in scope.variables
                         if v.name in self.outputs.keys()]
            leftover = set(self.outputs.values()).difference(v.name for v in variables)
            variables += [Variable(self.outputs[v.name], v.type_) for v in self.eval_lam.variables
                          if self.outputs.get(v.name) in leftover]
        else:
            variables = scope.variables
            scope_variable_names = set(v.name for v in variables)
            variables += [v for v in self.eval_lam.variables if v.name not in scope_variable_names]
        self.lam = context.temp_lambda(variables)
        self.lam.cloned_from = scope
        return self

    def execute(self, context):
        inp = self.lam.cloned_from.data
        equal_cols = list(self.equalities.items())
        to_merge = self.eval_lam.data.query(self.condition, engine='python')
        if len(self.outputs) > 0:
            to_merge = to_merge[set(list(self.outputs.keys()) + list(self.equalities.values()))]\
                        .rename(columns=self.outputs)
        left_col, right_col = equal_cols.pop()
        joined = inp.reset_index().merge(to_merge, left_on=left_col, right_on=right_col)
        joined = joined.set_index(self.lam.VAR_OID)
        condition = ' & '.join('({} == {})'.format(left_col, right_col) for left_col, right_col in equal_cols)
        if condition != '':
            results = joined.query(condition)
        else:
            results = joined
        self.lam.data = results
        return results


class AtomicEvaluationExpr(NormExpression):

    def __init__(self, lam, inputs, output_projection=None):
        """
        Evaluate the atomic function
        :param lam: the function to evaluate
        :param inputs: the input values
        :param output_projection: the output projection
        """
        super().__init__()
        from norm.models.norm import Lambda
        assert(lam is not None)
        assert(isinstance(lam, Lambda))
        assert(isinstance(inputs, dict))
        self.eval_lam: Lambda = lam
        self.lam: Lambda = None
        self.inputs: Dict = inputs
        self.output_projection: str = output_projection

    def __str__(self):
        return '{}({})'.format(self.eval_lam.signature, ', '.join('{}={}'.format(key, value) for key, value
                                                                  in self.inputs.items()))

    def compile(self, context):
        from norm.models import Variable, Lambda
        self.lam = context.temp_lambda([Variable(Lambda.VAR_OUTPUT, self.eval_lam.output_type)])
        if self.output_projection is None and self.projection is not None:
            self.output_projection = self.projection.variables[0].name
        return self

    def execute(self, context):
        inputs = dict((key, value.execute(context)) for key, value in self.inputs.items())
        result = self.eval_lam(**inputs)
        import numpy
        if self.output_projection is not None:
            if isinstance(result, (list, numpy.ndarray)):
                return Series(result, name=self.output_projection)
            elif isinstance(result, (Series, Index)):
                return result.rename(self.output_projection)
            elif isinstance(result, DataFrame):
                if len(result.columns) > 1:
                    cols = {col: '{}{}{}'.format(self.output_projection, self.VARIABLE_SEPARATOR, col)
                            for col in result.columns}
                    return result.loc[result.index.rename(self.output_projection)].rename(columns=cols)
                else:
                    result.columns = [self.output_projection]
                    return result
            else:
                return Series([result], name=self.output_projection)
        else:
            if isinstance(result, DataFrame) and len(result.columns) == 1:
                from norm.models import Lambda
                result.columns = [Lambda.VAR_OUTPUT]
            return result


class RetrievePartialDataExpr(NormExpression):

    def __init__(self, lam, outputs):
        """
        Retrieve all data from the given Lambda
        :param lam: the given Lambda
        :param outputs: the output projections
        """
        super().__init__()
        from norm.models.norm import Lambda
        assert(lam is not None)
        assert(isinstance(lam, Lambda))
        assert(not lam.atomic)
        self.eval_lam: Lambda = lam
        self.lam: Lambda = None
        self.outputs: Dict = outputs if outputs is not None else OrderedDict()

    def __str__(self):
        oid = self.eval_lam.VAR_OID
        out = self.eval_lam.VAR_OUTPUT
        return '{}({}){}'.format(self.eval_lam.signature,
                                 ', '.join(('{}?'.format(c) for c in self.outputs.keys() if c != oid and c != out)),
                                 '?' if self.outputs.get(oid) or self.outputs.get(out) else '')

    def _append_projection(self):
        if self.projection is not None:
            assert(len(self.projection.variables) <= 1)
            if self.projection.num == 1:
                new_lambda_name = self.projection.variables[0].name
            else:
                new_lambda_name = self.eval_lam.name
            outputs = OrderedDict((key, self.VARIABLE_SEPARATOR.join([new_lambda_name, value])) for key, value
                                  in self.outputs.items())
            if self.eval_lam.is_functional:
                outputs[self.eval_lam.VAR_OUTPUT] = new_lambda_name
            else:
                outputs[self.eval_lam.VAR_OID] = new_lambda_name
            self.outputs = outputs
            self.projection = None

    def compile(self, context):
        from norm.models import Lambda, Variable
        self._append_projection()

        if len(self.outputs) > 0:
            variables = [Variable(self.outputs[v.name], v.type_) for v in self.eval_lam.variables
                         if v.name in self.outputs.keys()]
        else:
            variables = self.eval_lam.variables
        self.lam = context.temp_lambda(variables)
        return self

    def execute(self, context):
        oid_output_col = self.outputs.get(self.eval_lam.VAR_OID)
        if oid_output_col is not None:
            del self.outputs[self.eval_lam.VAR_OID]

        result = self.eval_lam.data
        result = result[self.outputs.keys()].rename(columns=self.outputs)

        self.lam.data = result
        if oid_output_col is not None:
            result.index.rename(oid_output_col, inplace=True)
        return result


class RetrieveAllDataExpr(NormExpression):

    def __init__(self, lam, output_projection=None):
        """
        Retrieve all data from the given Lambda
        :param lam: the given Lambda
        :param output_projection: the output projection variable name
        """
        super().__init__()
        from norm.models.norm import Lambda
        assert(lam is not None)
        assert(isinstance(lam, Lambda))
        assert(not lam.atomic)
        self.eval_lam: Lambda = lam
        self.lam: Lambda = lam
        self.output_projection: str = output_projection

    def __str__(self):
        return '{}?'.format(self.lam.signature)

    def compile(self, context):
        return self

    def execute(self, context):
        if self.lam.is_functional:
            result = self.lam.data[self.lam.VAR_OUTPUT]
        else:
            result = self.lam.data.index
        if self.output_projection is not None:
            return result.rename(self.output_projection)
        else:
            return result


class AddDataEvaluationExpr(NormExpression):

    def __init__(self, lam, data, immediately=True):
        """
        Add data to a Lambda. If the lambda is not the current scope, revision occurs immediately. Otherwise,
        revision is delayed to TypeImplementation
        :param lam: the Lambda to add data
        :type lam: norm.model.norm.Lambda
        :param data: the data to add
        :type data: Dict
        :param immediately: whether to revise Lambda as a disjunction immediately, default to True
        :type immediately: bool
        """
        super().__init__()
        from norm.models.norm import Lambda
        self.lam: Lambda = lam
        self.data: Dict = data
        self.immediately: bool = immediately
        self.description: str = 'add data'
        self._query_str: str = None

    def __str__(self):
        if self._query_str is None:
            msg = "Need to execute first!"
            logger.error(msg)
            raise NormError(msg)
        return self._query_str

    def compile(self, context):
        if not self.immediately and len(self.data) == 1:
            expr = list(self.data.values())[0]
            from norm.executable.expression.arithmetic import ArithmeticExpr
            if isinstance(expr, ArithmeticExpr) and expr.op is not None:
                return expr
        return self

    def execute(self, context):
        if len(self.data) == 0:
            df = DataFrame(data=[self.lam.default])
            self._query_str = hash_df(df)
            return df

        from norm.executable.constant import Constant
        from norm.executable import NormExecutable
        data = OrderedDict((key, value.execute(context) if isinstance(value, (Constant, NormExecutable)) else value)
                           for key, value in self.data.items())
        data = self.unify(data)
        df = DataFrame(data=data, columns=data.keys())
        query_str = hash_df(df)
        self._query_str = query_str
        df = self.lam.fill_primary(df)
        df = self.lam.fill_time(df)
        df = self.lam.fill_oid(df)
        if self.lam.VAR_OID in df.columns:
            df = df.set_index(self.lam.VAR_OID)
        else:
            df.index.rename(self.lam.VAR_OID, inplace=True)
        if self.immediately:
            from norm.models.norm import RevisionType
            df = self.lam.revise(query_str, self.description, df, RevisionType.DISJUNCTION)
            if self.lam.is_functional:
                return df[self.lam.VAR_OUTPUT]
            else:
                return df.index
        return df


class ChainedEvaluationExpr(NormExpression):

    def __init__(self, lexpr, rexpr):
        """
        Chained evaluation expressions:
        Example:
        * a.b
        * a.test(sf, s)
        * a.b.c
        :param lexpr: base query expressions or chained expression
        :type lexpr: Union[VariableName, EvaluationExpr]
        :param rexpr: chained evaluation expression
        :type rexpr: Union[EvaluationExpr, VariableName]
        """
        super().__init__()
        self.lexpr = lexpr
        self.rexpr = rexpr

    def compile(self, context):
        if isinstance(self.rexpr, VariableName):
            if isinstance(self.lexpr, VariableName):
                return VariableName(self.lexpr, self.rexpr.name).compile(context)
            elif isinstance(self.lexpr, EvaluationExpr):
                if self.rexpr.name in self.lexpr.lam:
                    return ColumnVariable(self.lexpr, self.rexpr.name)
                else:
                    msg = '{} does not exist in the {}'.format(self.rexpr, self.lexpr)
                    logger.error(msg)
                    raise NormError(msg)
            else:
                msg = 'Only a variable or an evaluation can have chained operation for now, ' \
                      'but got {}'.format(self.lexpr)
                logger.error(msg)
                raise NormError(msg)
        elif isinstance(self.rexpr, EvaluationExpr):
            if self.rexpr.lam is None and isinstance(self.lexpr, ColumnVariable):
                return DataFrameColumnFunctionExpr(self.lexpr, self.rexpr).compile(context)
            else:
                # Evaluation with the previous expression as the first input argument
                self.rexpr.args = [ArgumentExpr(expr=self.lexpr)] + self.rexpr.args
                # Recompile the expression
                return self.rexpr.compile(context)
        else:
            msg = 'Only chaining on a variable or an evaluation, but got {}'.format(self.rexpr)
            logger.error(msg)
            raise NormError(msg)


class DataFrameColumnFunctionExpr(EvaluationExpr):

    AGG_FUNCS = {'abs', 'idxmax', 'idxmin', 'count', 'kurt', 'mad', 'max', 'min', 'median', 'mean', 'nunique', 'std',
                 'sum'}
    INT_FUNCS = {'idxmax', 'idxmin', 'count', 'nunique'}
    FLT_FUNCS = {'mean', 'std', 'kurt'}
    STR_FUNCS = {'capitalize', 'cat', 'pcount', 'contains', 'endswith', 'extract', 'extractall', 'find', 'findall',
                 'len', 'lower', 'match', 'replace', 'split', 'strip', 'title', 'upper', 'isalnum', 'isalpha', 'isdigit',
                 'isspace', 'islower', 'isupper', 'istitle', 'isnumeric', 'isdecimal', 'wrap', 'translate', 'swapcase',
                 'slice', 'slice_replace', 'repeat', 'pad', 'startswith', 'normalize'}

    def __init__(self, column_variable, expr, projection=None):
        super().__init__([])
        self.column_variable: ColumnVariable = column_variable
        self.expr: EvaluationExpr = expr
        self.projection: Projection = projection

    def __str__(self):
        return '{}{}{}'.format(self.column_variable.name, self.VARIABLE_SEPARATOR, self.expr.variable.name)

    @property
    def var_name(self):
        if self.projection is not None:
            assert(len(self.projection.variables) == 1)
            return self.projection.variables[0].name
        else:
            return str(self)

    def compile(self, context):
        self.eval_lam = self.column_variable.lam
        from norm.models.norm import Variable
        from norm.engine import QuantifiedLambda
        if isinstance(self.column_variable.lam, QuantifiedLambda):
            variables = self.column_variable.lam.get_grouped_variables()
        else:
            variables = []
        variables.append(Variable(self.var_name, self.var_type))
        self.lam = context.temp_lambda(variables=variables)
        return self

    @property
    def is_aggregation(self):
        return self.expr.variable.name in self.AGG_FUNCS

    @property
    def is_str_handling(self):
        return self.expr.variable.name in self.STR_FUNCS

    @property
    def var_type(self):
        from norm.models import lambdas
        f = self.expr.variable.name
        if self.is_aggregation:
            if f in self.INT_FUNCS:
                return lambdas.Integer
            if f in self.FLT_FUNCS:
                return lambdas.Float
            return self.column_variable.variable_type()
        if self.is_str_handling:
            return lambdas.String

    def get_args(self, context):
        args = []
        kwargs = {}
        for arg in self.expr.args:  # type: ArgumentExpr
            if arg.expr is None:
                continue
            if arg.op is None and arg.variable is not None:
                kwargs[arg.variable.name] = arg.expr.execute(context)
            else:
                args.append(arg.expr.execute(context))
        return args, kwargs

    def execute(self, context):
        args, kwargs = self.get_args(context)
        col = self.column_variable.execute(context)
        f = self.expr.variable.name
        if self.is_str_handling:
            df = getattr(col.str, f)(*args, **kwargs)
            if not isinstance(df, Series):
                df = Series(data=[df], name=self.var_name, dtype=self.var_type.dtype)
            else:
                df.name = self.var_name
        elif self.is_aggregation:
            df = getattr(col, f)(*args, **kwargs)
            from norm.engine import QuantifiedLambda
            if isinstance(self.column_variable.lam, QuantifiedLambda):
                df = DataFrame(data={self.var_name: df}).reset_index()
            else:
                df = Series(data=[df], name=self.var_name, dtype=self.var_type.dtype)
        else:
            msg = '{} is not implemented yet'.format(self.expr.variable.name)
            logging.error(msg)
            raise NormError(msg)
        self.lam.data = df
        return df
