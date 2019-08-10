import re

from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from dateutil import parser as dateparser
from textwrap import dedent

from norm import config
from norm.executable import NormExecutable
from norm.executable.command import Command
from norm.executable.schema.declaration import *
from norm.executable.expression.arithmetic import *
from norm.executable.expression.evaluation import *
from norm.executable.expression.query import *
from norm.executable.expression.slice import *
from norm.executable.expression.code import *
from norm.executable.schema.implementation import *
from norm.executable.schema.type import *
from norm.executable.schema.namespace import *
from norm.executable.schema.variable import UnquoteVariable
from norm.grammar.literals import AOP, COP, LOP, ImplType, ConstantType, MOP
from norm.grammar.normLexer import normLexer
from norm.grammar.normListener import normListener
from norm.grammar.normParser import normParser


class QType(Enum):
    FOREACH = 0
    FORANY = 1
    EXIST = 2


class QuantifiedLambda(object):

    def __init__(self, lam: Lambda):
        self.lam = lam
        self.cols = []
        self.quantifiers = []

    def __contains__(self, item):
        return item in self.lam

    @property
    def data(self):
        return self.lam.data.groupby(self.cols)

    def get_type(self, name):
        return self.lam.get_type(name)

    def get_grouped_variables(self):
        from norm.models import lambdas
        variables = dict((v.name, v) for v in self.lam.variables)
        return [variables.get(col, lambdas.Any) for col in self.cols]

    def add_cols(self, qtype, cols):
        pos = len(self.cols)
        self.cols.extend(cols)
        self.quantifiers.append((qtype, pos, pos + len(cols)))

    def quantify(self, df):
        if len(self.cols) == 0 or len(df) == 0:
            return df
        # assert(all([col in df.columns for col in self.cols]))
        while len(self.quantifiers) > 0:
            qtype, begin, end = self.quantifiers.pop()
            if len(df) == 0:
                continue
            if qtype == QType.EXIST:
                if begin == 0:
                    df = df.iloc[:1]
                else:
                    df = df.groupby(self.cols[:begin]).apply(lambda x: x.iloc[0]).reset_index(drop=True)
            elif qtype == QType.FORANY:
                total = len(self.lam.data[self.cols[begin:end]].drop_duplicates())
                if begin == 0:
                    df = df if len(df) == total else df.iloc[0:0]
                else:
                    df['_tmp_count'] = df.groupby(self.cols[:begin])[self.cols[begin]].transform('count')
                    df = df[df['_tmp_count'] == total].drop(columns=['_tmp_count'])
        return df


class ParseError(ValueError):
    pass


class NormErrorListener(ErrorListener):

    def __init__(self):
        super(NormErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        err_msg = "line " + str(line) + ":" + str(column) + " " + msg
        raise ParseError(err_msg)


error_listener = NormErrorListener()
walker = ParseTreeWalker()


class NormCompiler(normListener):
    TMP_VARIABLE_STUB = 'tmp_'

    def __init__(self, context_id, user, session=None):
        self.context_id = context_id
        self.scopes = []
        self.stack = []
        self.session = session
        self.user = user
        self.context_namespace = None
        self.user_namespace = None
        self.search_namespaces = None
        self.set_namespaces()
        self._python_context = {}

    def set_namespaces(self):
        if self.context_id:
            self.context_namespace = '{}.{}'.format(config.CONTEXT_NAMESPACE_STUB, self.context_id)
        if self.user:
            self.user_namespace = '{}.{}'.format(config.USER_NAMESPACE_STUB, self.user.username)
        from norm.models import NativeLambda, CoreLambda
        self.search_namespaces = [NativeLambda.NAMESPACE, CoreLambda.NAMESPACE, self.context_namespace,
                                  self.user_namespace]

    def set_temp_scope(self):
        """
        For a unnamed query, we assign a temporary type for the scope.
        For a named query, i.e., type implementation, the scope is the type.
        """
        self.scopes.append((self.temp_lambda([]), 'temp'))

    def get_scope(self, name):
        for scope, scope_lex in reversed(self.scopes):
            if name in scope:
                return scope
        return None

    @property
    def scope(self):
        return self.scopes[-1][0] if len(self.scopes) > 0 else None

    @property
    def scope_lex(self):
        return self.scopes[-1][1] if len(self.scopes) > 0 else None

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
        return self.stack[-1] if len(self.stack) > 0 else None

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

    def parse(self, script):
        if script is None or not isinstance(script, str):
            return None
        script = script.strip(' \r\n\t')
        if script == '':
            return None
        try:
            lexer = normLexer(InputStream(script))
            stream = CommonTokenStream(lexer)
            parser = normParser(stream)
            parser.addErrorListener(error_listener)
            return parser.script()
        except ParseError as e:
            msg = 'Can not parse {}'.format(script)
            logger.error(msg)
            logger.error(e)
            raise e

    def compile(self, script):
        tree = self.parse(script)
        if tree is not None:
            walker.walk(self, tree)
            return True
        else:
            return False
        # return self.optimize(self._pop())

    def temp_lambda(self, variables):
        return Lambda(self.context_namespace, self.TMP_VARIABLE_STUB + str(uuid.uuid4()), variables=variables)

    @property
    def python_context(self):
        return self._python_context

    @python_context.setter
    def python_context(self, python_context=None):
        if python_context is None:
            self._python_context = {}
        else:
            self._python_context.update(python_context)

    def execute(self, script):
        self.stack = []
        self.scopes = []
        if not self.compile(dedent(script)):
            return None

        results = None
        while len(self.stack) > 0:
            exe = self._pop()
            if isinstance(exe, NormExecutable):
                results = exe.execute(self)
            else:
                # TODO: shouldn't be here?
                results = exe
            if isinstance(results, Index) and isinstance(exe, NormExpression) and exe.lam is not None:
                results = exe.lam.data.loc[results]
        if isinstance(results, DataFrame):
            results.columns = results.columns.str.replace(NormExecutable.VARIABLE_SEPARATOR, '.')
        elif isinstance(results, Series):
            results = DataFrame(data={results.name.replace(NormExecutable.VARIABLE_SEPARATOR, '.'): results})
        return results

    def exitStatement(self, ctx: normParser.StatementContext):
        if ctx.typeDeclaration():
            if ctx.IMPL():
                query = self._pop()  # type: NormExpression
                type_declaration = self._pop()  # type: TypeDeclaration
                description = self._pop() if ctx.comments() else ''
                type_declaration.description = description
                op = ImplType(ctx.IMPL().getText())
                self._push(TypeImplementation(type_declaration, op, query, description).compile(self))
            elif ctx.comments():
                # otherwise just pass through
                type_declaration = self._pop()  # type: TypeDeclaration
                description = self._pop()
                type_declaration.description = description  # need to be recompiled
                self._push(type_declaration.compile(self))
        elif ctx.argumentDeclarations():
            args = self._pop()  # type: List[ArgumentDeclaration]
            type_ = self._pop()  # type: TypeName
            self._push(AdditionalTypeDeclaration(type_, args).compile(self))
        elif ctx.renames():
            renames = self._pop()  # type: List[RenameArgument]
            type_ = self._pop()  # type: TypeName
            self._push(RenameTypeDeclaration(type_, renames).compile(self))
        elif ctx.codeExpression():
            code: CodeExpr = self._pop()
            type_: TypeName = self._pop()
            description = self._pop() if ctx.comments() else ''
            op = ImplType(ctx.IMPL().getText())
            if type_.lam is None and op == ImplType.DEF:
                self._push(CodeTypeDeclaration(type_, code.code, description).compile(self))
            else:
                self._push(TypeImplementation(type_, op, code, description).compile(self))
        elif ctx.imports() or ctx.exports() or ctx.commands() or ctx.multiLineExpression():
            if ctx.comments():
                expr = self._pop()
                # ignore comments
                self._pop()
                self._push(expr)

    def exitNone(self, ctx: normParser.NoneContext):
        self._push(Constant(ConstantType.NULL, None))

    def exitBool_c(self, ctx: normParser.Bool_cContext):
        self._push(Constant(ConstantType.BOOL, ctx.getText().lower() == 'true'))

    def exitInteger_c(self, ctx: normParser.Integer_cContext):
        self._push(Constant(ConstantType.INT, int(ctx.getText())))

    def exitFloat_c(self, ctx: normParser.Float_cContext):
        self._push(Constant(ConstantType.FLT, float(ctx.getText())))

    def exitString_c(self, ctx: normParser.String_cContext):
        self._push(Constant(ConstantType.STR, str(ctx.getText()[1:-1])))

    def exitPattern(self, ctx: normParser.PatternContext):
        try:
            self._push(Constant(ConstantType.PTN, re.compile(str(ctx.getText()[2:-1]))))
        except:
            raise ParseError('Pattern constant {} is in wrong format, should be Python regex pattern'
                             .format(ctx.getText()))

    def exitUuid(self, ctx: normParser.UuidContext):
        self._push(Constant(ConstantType.UID, str(ctx.getText()[2:-1])))

    def exitUrl(self, ctx: normParser.UrlContext):
        self._push(Constant(ConstantType.URL, str(ctx.getText()[2:-1])))

    def exitDatetime(self, ctx: normParser.DatetimeContext):
        self._push(Constant(ConstantType.DTM, dateparser.parse(ctx.getText()[2:-1], fuzzy=True)))

    def exitConstant(self, ctx: normParser.ConstantContext):
        if ctx.LSBR() or ctx.LBR():
            constants = list(reversed([self._pop() for ch in ctx.children
                                       if isinstance(ch, normParser.ConstantContext)]))  # type: List[Constant]
            if ctx.LBR():
                self._push(TupleConstant(tuple(constant.type_ for constant in constants),
                                         tuple(constant.value for constant in constants)))
            else:
                types = set(constant.type_ for constant in constants)
                if len(types) > 1:
                    type_ = ConstantType.ANY
                else:
                    type_ = types.pop()
                self._push(ListConstant(type_, [constant.value for constant in constants]))

    def exitQueryProjection(self, ctx: normParser.QueryProjectionContext):
        variables = list(reversed([self._pop() for ch in ctx.children
                                   if isinstance(ch, normParser.VariableContext)]))
        self._push(Projection(variables))

    def exitComments(self, ctx: normParser.CommentsContext):
        spaces = ' \r\n\t'
        cmt = ctx.getText()
        if ctx.MULTILINE():
            cmt = cmt.strip(spaces)[2:-2].strip(spaces)
        elif ctx.SINGLELINE():
            cmt = '\n'.join(cmt_line.strip(spaces)[2:].strip(spaces) for cmt_line in cmt.split('\n'))
        self._push(cmt)

    def exitImports(self, ctx: normParser.ImportsContext):
        type_: TypeName = self._pop() if ctx.typeName() else None
        namespace = [str(v) for v in ctx.VARNAME()]
        variable = namespace.pop() if ctx.AS() else None
        self._push(Import('.'.join(namespace), type_, variable).compile(self))

    def exitExports(self, ctx: normParser.ExportsContext):
        type_: TypeName = self._pop()
        namespace = [str(v) for v in ctx.VARNAME()]
        variable = namespace.pop() if ctx.AS() else None
        self._push(Export('.'.join(namespace), type_, variable).compile(self))

    def exitCommands(self, ctx: normParser.CommandsContext):
        type_: TypeName = self._pop()
        op = MOP(ctx.SPACED_COMMAND().getText().strip().lower())
        self._push(Command(op, type_).compile(self))

    def exitArgumentDeclaration(self, ctx: normParser.ArgumentDeclarationContext):
        variable_property = ctx.argumentProperty().getText() if ctx.argumentProperty() else None
        optional = variable_property is not None and variable_property.lower().find('optional') >= 0
        as_oid = variable_property is not None and variable_property.lower().find('oid') >= 0
        as_time = variable_property is not None and variable_property.lower().find('time') >=0
        type_name: TypeName = self._pop()
        variable_name: VariableName = self._pop()
        self._push(ArgumentDeclaration(variable_name, type_name, optional, as_oid, as_time))

    def enterArgumentDeclarations(self, ctx: normParser.ArgumentDeclarationsContext):
        type_name = self._peek()
        if type_name is not None and isinstance(type_name, TypeName) and type_name.lam is not None:
            self.scopes.append((type_name.lam, 'argument_declarations'))

    def exitArgumentDeclarations(self, ctx: normParser.ArgumentDeclarationsContext):
        args = list(reversed([self._pop() for ch in ctx.children
                              if isinstance(ch, normParser.ArgumentDeclarationContext)]))
        self._push(args)
        if self.scope_lex == 'argument_declarations':
            self.scopes.pop()

    def exitRename(self, ctx: normParser.RenameContext):
        new_name: VariableName = self._pop()
        original_name: VariableName = self._pop()
        self._push(RenameArgument(original_name.name, new_name.name))

    def exitRenames(self, ctx: normParser.RenamesContext):
        args = list(reversed([self._pop() for ch in ctx.children
                              if isinstance(ch, normParser.RenameContext)]))
        self._push(args)
        if self.scope_lex == 'renames':
            self.scopes.pop()

    def enterRenames(self, ctx: normParser.RenamesContext):
        type_name = self._peek()
        if type_name is not None and isinstance(type_name, TypeName) and type_name.lam is not None:
            self.scopes.append((type_name.lam, 'renames'))

    def exitTypeDeclaration(self, ctx: normParser.TypeDeclarationContext):
        output_type_name = self._pop() if ctx.typeName(1) else None  # type: TypeName
        args = self._pop() if ctx.argumentDeclarations() else None  # type: List[ArgumentDeclaration]
        type_name = self._pop()  # type: TypeName
        self._push(TypeDeclaration(type_name, args, output_type_name).compile(self))

    def exitTypeName(self, ctx: normParser.TypeNameContext):
        typename = ctx.VARNAME()
        if typename:
            version = ctx.version().getText() if ctx.version() else None
            self._push(TypeName(str(typename), version).compile(self))
        elif ctx.LSBR():
            intern = self._pop()  # type: TypeName
            self._push(ListType(intern).compile(self))
        else:
            raise ParseError('Not a valid type name definition')

    def exitUnquote_variable(self, ctx:normParser.Unquote_variableContext):
        unqoted_variables = []
        template = []
        for ch in ctx.children:
            if isinstance(ch, normParser.VariableContext):
                variable: VariableName = self._pop()
                unqoted_variables.append(variable)
            else:
                template.append(ch.getText())
        self._push(UnquoteVariable(''.join(template), list(reversed(unqoted_variables))).compile(self))

    def exitVariable(self, ctx: normParser.VariableContext):
        if ctx.VARNAME():
            name = ctx.VARNAME().getText()
        elif ctx.COMMAND():
            name = ctx.COMMAND().getText()
        elif ctx.ARGOPT():
            name = ctx.ARGOPT().getText()
        else:
            name = None

        if ctx.DOT():
            # chained variable
            v: VariableName = self._pop()
            scope: VariableName = self._pop()
            self._push(VariableName(scope, v.name).compile(self))
        elif name is not None:
            self._push(VariableName(None, name).compile(self))

    def exitArgumentExpression(self, ctx: normParser.ArgumentExpressionContext):
        if isinstance(self._peek(), ArgumentExpr):
            return

        projection = self._pop() if ctx.queryProjection() else None  # type: Projection
        expr = self._pop() if ctx.arithmeticExpression() else None  # type: ArithmeticExpr
        op = COP(ctx.spacedConditionOperator().conditionOperator().getText().lower()) \
            if ctx.spacedConditionOperator() else None  # type: COP
        # = is treated as op is None
        variable = self._pop() if ctx.variable() else None  # type: VariableName
        if variable is None and projection is None and op is None and expr is not None \
                and isinstance(expr, EvaluationExpr) and isinstance(expr.variable, ColumnVariable) \
                and len(expr.args) == 0 and expr.projection is not None:
            self._push(ArgumentExpr(expr.variable, op, None, expr.projection).compile(self))
        else:
            self._push(ArgumentExpr(variable, op, expr, projection).compile(self))

    def enterArgumentExpressions(self, ctx: normParser.ArgumentExpressionsContext):
        expr = self._peek()
        if expr is not None and isinstance(expr, (VariableName, EvaluationExpr)) and expr.lam is not None:
            self.scopes.append((expr.lam, 'argument_expressions'))

    def exitArgumentExpressions(self, ctx: normParser.ArgumentExpressionsContext):
        args = list(reversed([self._pop() for ch in ctx.children
                              if isinstance(ch, normParser.ArgumentExpressionContext)]))
        self._push(args)
        if self.scope_lex == 'argument_expressions':
            self.scopes.pop()

    def enterMultiLineExpression(self, ctx: normParser.MultiLineExpressionContext):
        type_declaration = self._peek()
        if type_declaration is not None and isinstance(type_declaration, TypeDeclaration) \
                and type_declaration.lam is not None:
            self.scopes.append((type_declaration.lam, 'multiline'))

    def exitContext(self, ctx:normParser.ContextContext):
        if ctx.WITH():
            type_name = self._pop()
            self.scopes.append((type_name.lam, 'one_line_context'))
        elif ctx.FOREACH() or ctx.FORANY() or ctx.EXIST():
            if self.scope is not None and isinstance(self.scope, QuantifiedLambda):
                lam = self.scope
            else:
                lam = None
            tns = []
            for ch in ctx.children:
                if isinstance(ch, normParser.VariableContext):
                    tn = self._pop()
                    assert(isinstance(tn, ColumnVariable))
                    tns.append(tn.name)
                    if lam is None:
                        lam = tn.lam
                    else:
                        assert(tn.lam is lam)
            if not isinstance(lam, QuantifiedLambda):
                assert(lam is not None)
                lam = QuantifiedLambda(lam)
            if ctx.FOREACH():
                qtype = QType.FOREACH
            elif ctx.FORANY():
                qtype = QType.FORANY
            else:
                qtype = QType.EXIST
            lam.add_cols(qtype, list(reversed(tns)))
            if lam is not self.scope:
                self.scopes.append((lam, 'one_line_context'))

    def exitContextualOneLineExpression(self, ctx:normParser.ContextualOneLineExpressionContext):
        while self.scope_lex == 'one_line_context':
            scope, lex = self.scopes.pop()
            if isinstance(scope, QuantifiedLambda):
                expr = self._pop()  # type: NormExpression
                self._push(QuantifiedQueryExpr(expr, scope).compile(self))

    def exitMultiLineExpression(self, ctx: normParser.MultiLineExpressionContext):
        if ctx.newlineLogicalOperator():
            expr2 = self._pop()  # type: NormExpression
            expr1 = self._pop()  # type: NormExpression
            op = LOP.parse(ctx.newlineLogicalOperator().logicalOperator().getText())
            self._push(QueryExpr(op, expr1, expr2).compile(self))
        if self.scope_lex == 'multiline':
            self.scopes.pop()

    def enterSpacedLogicalOperator(self, ctx:normParser.SpacedLogicalOperatorContext):
        expr = self._peek()
        self.scopes.append((expr.lam, 'lop'))

    def enterNewlineLogicalOperator(self, ctx:normParser.NewlineLogicalOperatorContext):
        expr = self._peek()
        self.scopes.append((expr.lam, 'lop'))

    def exitOneLineExpression(self, ctx: normParser.OneLineExpressionContext):
        if ctx.queryProjection():
            projection: Projection = self._pop()
            expr = self._pop()
            if isinstance(expr, VariableName):
                expr = EvaluationExpr([], expr)
            elif isinstance(expr, Constant):
                expr = ConstantAssignmentExpr(expr)

            if projection.with_unquote:
                expr = PivotQueryExpr(expr, projection)
            else:
                expr.projection = projection
            self._push(expr.compile(self))
        elif ctx.NOT():
            expr = self._pop()  # type: NormExpression
            self._push(NegatedQueryExpr(expr).compile(self))
        elif ctx.spacedLogicalOperator():
            expr2 = self._pop()  # type: NormExpression
            expr1 = self._pop()  # type: NormExpression
            op = LOP.parse(ctx.spacedLogicalOperator().logicalOperator().getText())
            self._push(QueryExpr(op, expr1, expr2).compile(self))
            if self.scope_lex == 'lop':
                self.scopes.pop()
        elif isinstance(self._peek(), TupleConstant):
            expr = self._pop()
            lam = self.scope
            values = expr.value
            from norm.models.norm import Lambda
            from norm.models import lambdas
            variables = [v.name for v in lam.variables]
            nanonymous = len(values) - len(variables)
            variables.extend('{}{}'.format(Lambda.VAR_ANONYMOUS_STUB, i) for i in range(nanonymous))
            data = dict((name, value) for name, value in zip(variables, values))
            self._push(AddDataEvaluationExpr(lam, data, False))

    def exitConditionExpression(self, ctx: normParser.ConditionExpressionContext):
        if ctx.spacedConditionOperator():
            qexpr = self._pop()  # type: ArithmeticExpr
            aexpr = self._pop()  # type: ArithmeticExpr
            cop = COP(ctx.spacedConditionOperator().conditionOperator().getText().lower())
            self._push(ConditionExpr(cop, aexpr, qexpr).compile(self))

    def exitArithmeticExpression(self, ctx: normParser.ArithmeticExpressionContext):
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
            if isinstance(expr2, ArgumentExpr):
                expr2 = expr2.variable
            expr1 = self._pop() if ctx.arithmeticExpression(1) else None  # type: ArithmeticExpr
            if isinstance(expr1, AddDataEvaluationExpr):
                expr1 = list(expr1.data.values())[0]
                assert (isinstance(expr1, ArithmeticExpr))
            self._push(ArithmeticExpr(op, expr1, expr2).compile(self))

    def exitSlicedExpression(self, ctx: normParser.SlicedExpressionContext):
        if ctx.LSBR():
            if ctx.evaluationExpression(1):
                expr_range = self._pop()  # type: NormExpression
                expr = self._pop()  # type: NormExpression
                self._push(EvaluatedSliceExpr(expr, expr_range).compile(self))
            else:
                end = self._pop() if ctx.integer_c(1) else None  # type: Constant
                start = self._pop() if ctx.integer_c(0) else None  # type: Constant
                expr = self._pop()
                start_value = start.value
                if end is not None:
                    end_value = end.value
                elif ctx.COLON():
                    colon_before_number = True
                    for ch in ctx.children:
                        if ch == ctx.COLON():
                            break
                        elif ch == ctx.integer_c(0):
                            colon_before_number = False
                            break
                    if colon_before_number:
                        end_value = start_value
                        start_value = 0
                    else:
                        end_value = None
                else:
                    end_value = start_value + 1
                self._push(SliceExpr(expr, start_value, end_value).compile(self))

    def exitEvaluationExpression(self, ctx: normParser.EvaluationExpressionContext):
        if ctx.DOT():
            rexpr = self._pop()
            lexpr = self._pop()
            self._push(ChainedEvaluationExpr(lexpr, rexpr).compile(self))
        elif ctx.argumentExpressions():
            args = self._pop() if ctx.argumentExpressions() else []  # type: List[ArgumentExpr]
            variable = self._pop() if ctx.variable() else None  # type: VariableName
            self._push(EvaluationExpr(args, variable, None).compile(self))

    def exitCodeExpression(self, ctx: normParser.CodeExpressionContext):
        self._push(CodeExpr(ctx.code().getText()).compile(self))
