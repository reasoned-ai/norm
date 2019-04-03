from pandas import DataFrame

from norm.grammar.literals import COP

from norm.executable import NormError
from norm.executable.expression.argument import ArgumentExpr
from norm.executable.schema.variable import VariableName, ColumnVariable
from norm.executable.expression import NormExpression

from typing import List, Dict

import logging
logger = logging.getLogger(__name__)


class EvaluationExpr(NormExpression):

    def __init__(self, args, variable=None):
        """
        The evaluation of an expression either led by a variable name
        :param args: the arguments provided
        :type args: List[ArgumentExpr]
        :param variable: the variable name to evaluate
        :type variable: VariableName
        """
        super().__init__()
        self.variable: VariableName = variable
        self.args: List[ArgumentExpr] = args
        self.inputs: Dict[str, DataFrame] = None
        self.outputs: Dict[str, str] = None
        self.is_to_add_data: bool = False
        from norm.models.norm import Lambda
        self.lam: Lambda = None

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
            return {arg.variable.name if arg.variable else '{}{}'.format(Lambda.VAR_ANONYMOUS_STUB, i): arg.expr
                    for i, arg in enumerate(self.args)}

        keyword_arg = False
        inputs = {}
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
        outputs = {}
        from norm.models.norm import Variable
        for ov, arg in zip(lam.variables, self.args):  # type: Variable, ArgumentExpr
            if arg.projection is not None:
                assert (len(arg.projection.variables) <= 1)
                assert (not arg.projection.to_evaluate)
                if arg.variable is None:
                    outputs[ov.name] = arg.projection.variables[0].name
                else:
                    if len(arg.projection.variables) == 0:
                        outputs[arg.variable.name] = arg.variable.name
                    else:
                        outputs[arg.variable.name] = arg.projection.variables[0].name
        return outputs

    def compile(self, context):
        if self.variable is None:
            from norm.models.norm import Lambda
            assert(context.scope is not None)
            assert(isinstance(context.scope, Lambda))
            lam = context.scope
            # constructing new objects
            assert(self.check_assignment_arguments())
            self.is_to_add_data = True
            self.inputs = self.build_assignment_inputs(lam)
            self.outputs = None
        else:
            lam = self.variable.lam
            if lam is None:
                # Might need to be combined with previous context
                return self
            if self.check_assignment_arguments():
                self.inputs = self.build_assignment_inputs(lam)
            else:
                self.inputs = self.build_conditional_inputs()
            self.outputs = self.build_outputs(lam)
        self.lam = lam
        return self

    def execute(self, context):
        if isinstance(self.inputs, dict):
            inputs = dict((key, value.execute(context)) for key, value in self.inputs.items())
            if len(inputs) == 0:
                if self.lam.atomic:
                    return self.lam()
                else:
                    df = self.lam.df
            elif self.is_to_add_data:
                cols = list(sorted(inputs.keys()))
                return DataFrame(data=inputs, columns=cols)
            elif self.lam.atomic:
                df = self.lam(**inputs)
            else:
                # Simply creating new objects
                # TODO: do we need oids for these?
                df = self.unify(inputs)
        else:
            df = self.lam.data.query(self.inputs, engine='python')

        if isinstance(df, DataFrame):
            if len(self.outputs) > 0:
                df = df[list(sorted(self.outputs.keys()))].rename(columns=self.outputs)
            else:
                df = df[[v.name for v in self.lam.variables if v.name in df.columns]]
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
            df = getattr(col.str, func)(*args, **kwargs)
        return df
