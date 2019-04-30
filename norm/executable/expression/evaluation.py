from time import sleep

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
        self.joins: List[JoinVariable] = []
        from norm.models.norm import Lambda
        self.lam: Lambda = None
        self.projection: Projection = projection

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
        inputs = []
        for arg in self.args:
            if arg.op is None or arg.expr is None:
                continue
            if isinstance(arg.variable, JoinVariable):
                self.joins.append(arg.variable)
            if arg.op == COP.LK:
                condition = '{}.str.contains({})'.format(arg.variable, arg.expr)
            else:
                condition = '{} {} ({})'.format(arg.variable, arg.op, arg.expr)
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
                assert(not arg.projection.to_evaluate)
                if arg.variable is None:
                    outputs[ov.name] = arg.projection.variables[0].name
                else:
                    if len(arg.projection.variables) == 0:
                        outputs[arg.variable.name] = arg.variable.name
                    else:
                        outputs[arg.variable.name] = arg.projection.variables[0].name
        if self.projection is not None:
            assert(len(self.projection.variables) <= 1)
            assert(not self.projection.to_evaluate)
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

        if is_to_add_data:
            return AddDataEvaluationExpr(lam, self.inputs, self.variable is not None)
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
        self.lam = lam
        return self

    def execute(self, context):
        for jv in self.joins:
            jv.execute(context)
        df = self.lam.data.query(self.inputs, engine='python')

        if isinstance(df, DataFrame) and len(self.outputs) > 0:
            df = df[self.outputs.keys()].rename(columns=self.outputs)

        return df


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
        self.lam: Lambda = lam
        self.output_lam: Lambda = self.lam.output_type
        self.inputs: Dict = inputs
        self.output_projection: str = output_projection

    def __str__(self):
        return '{}({})'.format(self.lam.signature, ', '.join('{}={}'.format(key, value) for key, value
                                                             in self.inputs.items()))

    def compile(self, context):
        return self

    def execute(self, context):
        inputs = dict((key, value.execute(context)) for key, value in self.inputs.items())
        result = self.lam(**inputs)
        if self.output_projection is not None:
            if isinstance(result, (Series, Index)):
                return result.rename(self.output_projection)
            elif isinstance(result, DataFrame):
                cols = {col: '{}{}{}'.format(self.output_projection, self.VARIABLE_SEPARATOR, col)
                        for col in result.columns}
                return result.loc[result.index.rename(self.output_projection)].rename(columns=cols)
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
        self.lam: Lambda = lam
        self.output_lam: Lambda = self.lam.output_type
        self.outputs: Dict = outputs

    def __str__(self):
        oid = self.lam.VAR_OID
        out = self.lam.VAR_OUTPUT
        return '{}({}){}'.format(self.lam.signature,
                                 ', '.join(('{}?'.format(c) for c in self.outputs.keys() if c != oid and c != out)),
                                 '?' if self.outputs.get(oid) or self.outputs.get(out) else '')

    def compile(self, context):
        return self

    def execute(self, context):
        output_col = self.outputs.get(self.lam.VAR_OID) or self.outputs.get(self.lam.VAR_OUTPUT)
        if not self.lam.is_functional and output_col is not None:
            result = self.lam.data.reset_index()
        else:
            result = self.lam.data

        result = result[self.outputs.keys()].rename(columns=self.outputs)

        if output_col is not None:
            result = result.set_index(output_col)

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
        self.lam: Lambda = lam
        self.output_lam: Lambda = self.lam.output_type
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
        self.output_lam: Lambda = self.lam.output_type
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
        return self

    def execute(self, context):
        if len(self.data) == 0:
            return DataFrame(data=[self.lam.default])

        data = OrderedDict((key, value.execute(context)) for key, value in self.data.items())
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

    def __init__(self, column_variable, expr):
        super().__init__([])
        self.column_variable: ColumnVariable = column_variable
        self.expr: EvaluationExpr = expr

    def compile(self, context):
        return self

    def execute(self, context):
        col = self.column_variable.scope.lam.data[self.column_variable.name]
        print(self.column_variable.scope.lam)
        args = []
        kwargs = {}
        for arg in self.expr.args:  # type: ArgumentExpr
            if arg.expr is None:
                continue
            if arg.op is None and arg.variable is not None:
                kwargs[arg.variable.name] = arg.expr.execute(context)
            else:
                args.append(arg.expr.execute(context))
        func = self.expr.variable.name
        try:
            df = getattr(col, func)(*args, **kwargs)
        except:
            print('error on {}'.format(col))
            df = getattr(col.str, func)(*args, **kwargs)
            print(args, kwargs)
            print(df)
        return df
