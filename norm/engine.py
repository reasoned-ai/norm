import re
import uuid

from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from dateutil import parser as dateparser
from functools import lru_cache
from textwrap import dedent
from typing import List

from norm import config
from norm.executable import Constant, Projection, NormExecutable, ListConstant
from norm.executable.declaration import *
from norm.executable.expression.arithmetic import *
from norm.executable.expression.code import *
from norm.executable.expression.condition import *
from norm.executable.expression.evaluation import *
from norm.executable.expression.query import *
from norm.executable.expression.slice import *
from norm.executable.implementation import *
from norm.executable.type import *
from norm.executable.namespace import *
from norm.literals import AOP, COP, LOP, ImplType, CodeMode, ConstantType
from norm.models import CoreLambda
from norm.utils import current_user
from norm.normLexer import normLexer
from norm.normListener import normListener
from norm.normParser import normParser


class ParseError(ValueError):
    pass


class NormErrorListener(ErrorListener):

    def __init__(self):
        super(NormErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        err_msg = "line " + str(line) + ":" + str(column) + " " + msg
        raise ValueError(err_msg)


walker = ParseTreeWalker()


class NormCompiler(normListener):
    TMP_VARIABLE_STUB = 'tmp_'

    def __init__(self, context_id):
        # TODO: make sure the context can be save/load from cache
        # context_id, user, namespaces should be able to be cached directly
        # scope, stack and session should be reset
        self.context_id = context_id
        self.scope = None  # type: Lambda
        self.stack = []
        self.session = None
        self.user = None
        self.context_namespace = None
        self.user_namespace = None
        self.search_namespaces = None
        self.set_namespaces()

    def set_namespaces(self):
        self.user = current_user()
        self.context_namespace = '{}.{}'.format(config.CONTEXT_NAMESPACE_STUB, self.context_id)
        self.user_namespace = '{}.{}'.format(config.USER_NAMESPACE_STUB, self.user.username)
        from norm.models import NativeLambda
        self.search_namespaces = {NativeLambda.NAMESPACE, CoreLambda.NAMESPACE, self.context_namespace,
                                  self.user_namespace}

    def set_session(self, session):
        """
        Set the db session
        :param session: the db session
        :type session: sqlalchemy.session
        """
        self.session = session
        self.scope = None
        self.stack = []

    def set_temp_scope(self):
        """
        For a unnamed query, we assign a temporary type for the scope.
        For a named query, i.e., type implementation, the scope is the type.
        :return:
        """
        self.scope = Lambda(self.context_namespace, self.TMP_VARIABLE_STUB + str(uuid.uuid4()))

    def _push(self, exe):
        self.stack.append(exe)

    def _pop(self):
        """
        :rtype: NormExecutable
        """
        return self.stack.pop()

    def _peek(self):
        """
        :rtype: NormExecutable
        """
        return self.stack[-1]

    def optimize(self, exe):
        """
        Optimize the AST to have a more efficient execution plan
        # TODO: optimization strategies
        * Filtering conditions can be combined and executed in batch instead of sequential
        * Arithmetic equations can be combined and passed to DF in batch instead of sequential
        :param exe: the executable to be optimized
        :type exe: NormExecutable
        :return: the optimized executable
        :rtype: NormExecutable
        """
        return exe

    def compile(self, script):
        if script is None or not isinstance(script, str):
            return None
        script = script.strip(' \r\n\t')
        if script == '':
            return None

        lexer = normLexer(InputStream(script))
        stream = CommonTokenStream(lexer)
        parser = normParser(stream)
        parser.addErrorListener(NormErrorListener())
        tree = parser.script()
        walker.walk(self, tree)
        # assert(len(self.stack) == 1)  # Ensure that parsing and compilation has finished completely

        # return self.optimize(self._pop())
        return

    def execute(self, script):
        self.compile(dedent(script))
        results = None
        while len(self.stack) > 0:
            exe = self._pop()
            if isinstance(exe, NormExecutable):
                results = exe.execute(self)
            else:
                # TODO: shouldn't be here
                results = exe
        return results

    def exitStatement(self, ctx:normParser.StatementContext):
        if ctx.typeDeclaration():
            type_declaration = self._pop()
            description = self._pop() if ctx.comments() else ''
            type_declaration.description = description
            self._push(type_declaration)
        elif ctx.typeName():
            query = self._pop()  # type: NormExpression
            type_name = self._pop()
            description = self._pop() if ctx.comments() else ''
            if ctx.OR():
                op = ImplType.OR_DEF
            elif ctx.AND():
                op = ImplType.AND_DEF
            elif ctx.COLON():
                op = ImplType.DEF
            else:
                msg = 'Currently only support :=, |=, &= for implementation'
                logger.error(msg)
                raise NormError(msg)
            self._push(TypeImplementation(type_name, op, query, description).compile(self))
        elif ctx.imports() or ctx.exports() or ctx.multiLineExpression():
            if ctx.comments():
                expr = self._pop()
                # ignore comments
                self._pop()
                self._push(expr)

    def exitNone(self, ctx:normParser.NoneContext):
        self._push(Constant(ConstantType.NULL, None).compile(self))

    def exitBool_c(self, ctx:normParser.Bool_cContext):
        self._push(Constant(ConstantType.BOOL, ctx.getText().lower() == 'true').compile(self))

    def exitInteger_c(self, ctx:normParser.Integer_cContext):
        self._push(Constant(ConstantType.INT, int(ctx.getText())).compile(self))

    def exitFloat_c(self, ctx:normParser.Float_cContext):
        self._push(Constant(ConstantType.FLT, float(ctx.getText())).compile(self))

    def exitString_c(self, ctx:normParser.String_cContext):
        self._push(Constant(ConstantType.STR, str(ctx.getText()[1:-1])).compile(self))

    def exitPattern(self, ctx:normParser.PatternContext):
        try:
            self._push(Constant(ConstantType.PTN, re.compile(str(ctx.getText()[2:-1]))).compile(self))
        except:
            raise ParseError('Pattern constant {} is in wrong format, should be Python regex pattern'
                             .format(ctx.getText()))

    def exitUuid(self, ctx:normParser.UuidContext):
        self._push(Constant(ConstantType.UID, str(ctx.getText()[2:-1])).compile(self))

    def exitUrl(self, ctx:normParser.UrlContext):
        self._push(Constant(ConstantType.URL, str(ctx.getText()[2:-1])).compile(self))

    def exitDatetime(self, ctx:normParser.DatetimeContext):
        self._push(Constant(ConstantType.DTM, dateparser.parse(ctx.getText()[2:-1], fuzzy=True)).compile(self))

    def exitConstant(self, ctx:normParser.ConstantContext):
        if ctx.LSBR():
            constants = list(reversed([self._pop() for ch in ctx.children
                                       if isinstance(ch, normParser.ConstantContext)]))  # type: List[Constant]
            types = set(constant.type_ for constant in constants)
            if len(types) > 1:
                type_ = ConstantType.ANY
            else:
                type_ = types.pop()
            self._push(ListConstant(type_, constants).compile(self))

    def exitQueryProjection(self, ctx:normParser.QueryProjectionContext):
        variables = list(reversed([self._pop() for ch in ctx.children
                                   if isinstance(ch, normParser.VariableContext)]))
        to_evaluate = True if ctx.LCBR() else False
        # TODO: evaluate the variables to get the referred variables
        self._push(Projection(variables, to_evaluate))

    def exitComments(self, ctx:normParser.CommentsContext):
        spaces = ' \r\n\t'
        cmt = ctx.getText()
        if ctx.MULTILINE():
            cmt = cmt.strip(spaces)[2:-2].strip(spaces)
        elif ctx.SINGLELINE():
            cmt = '\n'.join(cmt_line.strip(spaces)[2:].strip(spaces) for cmt_line in cmt.split('\n'))
        self._push(cmt)

    def exitImports(self, ctx:normParser.ImportsContext):
        type_ = self._pop() if ctx.typeName() else None   # type: TypeName
        namespace = [str(v) for v in ctx.VARNAME()]
        variable = namespace.pop() if ctx.AS() else None
        self._push(Import('.'.join(namespace), type_, variable).compile(self))

    def exitExports(self, ctx:normParser.ExportsContext):
        type_ = self._pop()  # type: TypeName
        namespace = [str(v) for v in ctx.VARNAME()]
        variable = namespace.pop() if ctx.AS() else None
        self._push(Export('.'.join(namespace), type_, variable).compile(self))

    def exitArgumentDeclaration(self, ctx:normParser.ArgumentDeclarationContext):
        type_name = self._pop()  # type: TypeName
        variable_name = self._pop()  # type: VariableName
        self._push(ArgumentDeclaration(variable_name, type_name).compile(self))

    def exitArgumentDeclarations(self, ctx:normParser.ArgumentDeclarationsContext):
        args = list(reversed([self._pop() for ch in ctx.children
                             if isinstance(ch, normParser.ArgumentDeclarationContext)]))
        self._push(args)

    def exitTypeDeclaration(self, ctx:normParser.TypeDeclarationContext):
        output_type_name = self._pop() if ctx.typeName(1) else None  # type: TypeName
        args = self._pop() if ctx.argumentDeclarations() else None  # type: List[ArgumentDeclaration]
        type_name = self._pop()  # type: TypeName
        self._push(TypeDeclaration(type_name, args, output_type_name).compile(self))

    def exitTypeName(self, ctx:normParser.TypeNameContext):
        typename = ctx.VARNAME()
        if typename:
            version = int(ctx.version().getText()[1:]) if ctx.version() else None
            self._push(TypeName(str(typename), version).compile(self))
        elif ctx.LSBR():
            intern = self._pop()  # type: TypeName
            self._push(ListType(intern).compile(self))
        else:
            raise ParseError('Not a valid type name definition')

    def exitVariable(self, ctx:normParser.VariableContext):
        name = ctx.VARNAME().getText()  # type: str
        scope = self._pop() if ctx.variable() else None  # type: VariableName
        self._push(VariableName(scope, name).compile(self))

    def exitArgumentExpression(self, ctx:normParser.ArgumentExpressionContext):
        projection = self._pop() if ctx.queryProjection() else None  # type: Projection
        expr = self._pop() if ctx.arithmeticExpression() else None  # type: ArithmeticExpr
        op = COP(ctx.spacedConditionOperator().conditionOperator().getText().lower()) \
            if ctx.spacedConditionOperator() else None  # type: COP
        # = is treated as op is None
        variable = self._pop() if ctx.variable() else None  # type: VariableName
        self._push(ArgumentExpr(variable, op, expr, projection).compile(self))

    def exitArgumentExpressions(self, ctx:normParser.ArgumentExpressionsContext):
        args = list(reversed([self._pop() for ch in ctx.children
                             if isinstance(ch, normParser.ArgumentExpressionContext)]))
        self._push(args)

    def exitMultiLineExpression(self, ctx:normParser.MultiLineExpressionContext):
        if ctx.newlineLogicalOperator():
            expr2 = self._pop()  # type: NormExpression
            expr1 = self._pop()  # type: NormExpression
            op = LOP.parse(ctx.newlineLogicalOperator().logicalOperator().getText())
            self._push(QueryExpr(op, expr1, expr2).compile(self))

    def exitOneLineExpression(self, ctx:normParser.OneLineExpressionContext):
        if ctx.queryProjection():
            projection = self._pop()
            expr = self._peek()
            expr.projection = projection
        elif ctx.NOT():
            expr = self._pop()  # type: NormExpression
            self._push(NegatedQueryExpr(expr).compile(self))
        elif ctx.spacedLogicalOperator():
            expr2 = self._pop()  # type: NormExpression
            expr1 = self._pop()  # type: NormExpression
            op = LOP.parse(ctx.spacedLogicalOperator().logicalOperator().getText())
            self._push(QueryExpr(op, expr1, expr2).compile(self))

    def exitConditionExpression(self, ctx:normParser.ConditionExpressionContext):
        if ctx.spacedConditionOperator():
            qexpr = self._pop()  # type: ArithmeticExpr
            aexpr = self._pop()  # type: ArithmeticExpr
            cop = COP(ctx.spacedConditionOperator().conditionOperator().getText().lower())
            self._push(ConditionExpr(cop, aexpr, qexpr).compile(self))

    def exitArithmeticExpression(self, ctx:normParser.ArithmeticExpressionContext):
        if ctx.slicedExpression():
            return

        op = None
        if ctx.MOD():
            op = AOP.MOD
        elif ctx.EXP():
            op = AOP.EXP
        elif ctx.TIMES():
            op = AOP.MUL
        elif ctx.DIVIDE():
            op = AOP.DIV
        elif ctx.PLUS():
            op = AOP.ADD
        elif ctx.MINUS():
            op = AOP.SUB

        if op is not None:
            expr2 = self._pop()  # type: ArithmeticExpr
            expr1 = self._pop() if ctx.arithmeticExpression(1) else None  # type: ArithmeticExpr
            self._push(ArithmeticExpr(op, expr1, expr2).compile(self))

    def exitSlicedExpression(self, ctx:normParser.SlicedExpressionContext):
        if ctx.LSBR():
            if ctx.evaluationExpression(1):
                expr_range = self._pop()  # type: NormExpression
                expr = self._pop()  # type: NormExpression
                self._push(EvaluatedSliceExpr(expr, expr_range).compile(self))
            else:
                end = self._pop() if ctx.integer_c(1) else None  # type: Constant
                start = self._pop() if ctx.integer_c(0) else None  # type: Constant
                expr = self._pop()
                self._push(SliceExpr(expr, start.value, end.value).compile(self))

    def exitEvaluationExpression(self, ctx:normParser.EvaluationExpressionContext):
        if ctx.DOT():
            rexpr = self._pop()
            lexpr = self._pop()
            self._push(ChainedEvaluationExpr(lexpr, rexpr).compile(self))
        elif ctx.argumentExpressions():
            args = self._pop()  # type: List[ArgumentExpr]
            variable = self._pop() if ctx.variable() else None  # type: VariableName
            self._push(EvaluationExpr(args, variable).compile(self))

    def exitCodeExpression(self, ctx:normParser.CodeExpressionContext):
        if ctx.PYTHON_BLOCK():
            self._push(CodeExpr(CodeMode.PYTHON, ctx.code().getText()).compile(self))
        elif ctx.SQL_BLOCK():
            self._push(CodeExpr(CodeMode.SQL, ctx.code().getText()).compile(self))
        else:
            self._push(CodeExpr(CodeMode.QUERY, ctx.code().getText()).compile(self))


@lru_cache(maxsize=128)
def get_compiler(context_id):
    """
    Get the compiler with respect to the context id
    :param context_id: the id for the context
    :type context_id: int
    :return: a norm compiler
    :rtype: NormCompiler
    """
    return NormCompiler(context_id)


def executor(context_id, session):
    compiler = get_compiler(context_id)
    compiler.set_session(session)
    return compiler
