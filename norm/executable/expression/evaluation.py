from pandas import DataFrame

from norm.grammar.literals import COP

from norm.executable import NormError, Constant
from norm.executable.expression.argument import ArgumentExpr
from norm.executable.variable import VariableName, ColumnVariable
from norm.executable.expression import NormExpression

from hashids import Hashids
from typing import List

import logging

from norm.utils import hash_df

logger = logging.getLogger(__name__)

h = Hashids()


class EvaluationExpr(NormExpression):

    def serialize(self):
        pass

    def __init__(self, args, variable=None):
        """
        The evaluation of an expression either led by a variable name
        :param args: the arguments provided
        :type args: List[ArgumentExpr]
        :param variable: the variable name to evaluate
        :type variable: VariableName
        """
        super().__init__()
        self.variable = variable
        self.args = args
        self.inputs = None
        self.outputs = None
        from norm.models.norm import Lambda
        self.lam = None   # type: Lambda
        self.is_to_add_data = False

    @property
    def is_constant_arguments(self):
        return all(isinstance(arg.expr, Constant) for arg in self.args)

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

    def build_assignment_inputs(self):
        """
        If the arguments are in assignment style, build the inputs as assignments
        :return: a dictionary mapping from a variable to an expression for the inputs
        :rtype: Dict
        """
        assert(self.lam is not None)
        if self.lam.nargs == 0:
            # Lambda is anonymously created
            from norm.models.norm import Lambda
            return {arg.variable.name if arg.variable else '{}{}'.format(Lambda.VAR_ANONYMOUS_STUB, i): arg.expr
                    for i, arg in enumerate(self.args)}

        nargs = len(self.args)
        assert(nargs <= self.lam.nargs)
        keyword_arg = False
        inputs = {}
        from norm.models.norm import Variable
        for ov, arg in zip(self.lam.variables[:nargs], self.args):  # type: Variable, ArgumentExpr
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
        assert(self.lam is not None)
        inputs = []
        for arg in self.args:
            if arg.op is None or arg.expr is None:
                continue
            # arg.expr should have been compiled
            if arg.op == COP.LK:
                condition = '{}.str.contains({})'.format(arg.variable, arg.expr)
            else:
                condition = '{} {} ({})'.format(arg.variable, arg.op, arg.expr)
            inputs.append(condition)
        return ' and '.join(inputs)

    def build_outputs(self):
        """
        Build the outputs according to the projection
        :return: a dictionary mapping from the original variable to the new variable
        :rtype: Dict
        """
        assert(self.lam is not None)
        nargs = len(self.args)
        # assert(nargs <= self.lam.nargs)
        outputs = {}
        from norm.models.norm import Variable
        for ov, arg in zip(self.lam.variables[:nargs], self.args):  # type: Variable, ArgumentExpr
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
            self.lam = context.scope  # norm.models.norm.Lambda
            # constructing new objects
            assert(self.check_assignment_arguments())
            self.is_to_add_data = True
            self.inputs = self.build_assignment_inputs()
            self.outputs = None
        else:
            self.lam = self.variable.lam
            if self.lam is None:
                # Might need to be combined with previous context
                return self
            if self.check_assignment_arguments():
                self.inputs = self.build_assignment_inputs()
            else:
                self.inputs = self.build_conditional_inputs()
            self.outputs = self.build_outputs()
        return self

    def execute(self, context):
        if isinstance(self.inputs, dict):
            inputs = dict((key, value.execute(context)) for key, value in self.inputs.items())
        else:
            inputs = self.inputs
        if self.is_to_add_data:
            cols = list(sorted(inputs.keys()))
            df = DataFrame(data=inputs, columns=cols)
            self.lam.add_data(hash_df(df), df)
            return self.lam
        lam = self.lam.query(inputs, self.outputs)
        if self.projection and len(self.projection.variables) > 0:
            assert(len(lam.df.columns) == len(self.projection.variables))
            renames = {old_col: new_col.name for old_col, new_col in zip(lam.df.columns, self.projection.variables)}
            lam.rename_variable(renames)
        return lam


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
        self.lam = None

    def serialize(self):
        pass

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
                self.rexpr.args = [ArgumentExpr(None, None, self.lexpr, None)] + self.rexpr.args
                # Recompile the expression
                return self.rexpr.compile(context)
        else:
            msg = 'Only chaining on a variable or an evaluation, but got {}'.format(self.rexpr)
            logger.error(msg)
            raise NormError(msg)

    def execute(self, context):
        return self.lam


class DataFrameColumnFunctionExpr(EvaluationExpr):

    def __init__(self, column_variable, expr):
        super().__init__([], None)
        self.column_variable = column_variable  # type: ColumnVariable
        self.expr = expr  # type: EvaluationExpr

    def compile(self, context):
        return self

    def execute(self, context):
        lam = self.column_variable.scope.lam.clone()
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
            lam.df = getattr(col, func)(*args, **kwargs)
        except:
            lam.df = getattr(col.str, func)(*args, **kwargs)
        return lam
