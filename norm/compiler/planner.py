import re
import zlib

import numpy as np
from dateutil import parser as dateparser
from textwrap import dedent

from norm import config
from norm.executable import NormExecutable
from norm.compiler import *
from norm.grammar.normParser import normParser
from norm.grammar.normListener import normListener


class NormPlanner(object):
    TMP_VARIABLE_STUB = 'tmp_'
    THAT_VARIABLE_NAME = 'that'
    VARIABLE_SEPARATOR = '__dot__'

    def __init__(self, module, session, context):
        self.module = module
        self.session = session
        self.context = context
        self.scopes = []
        self.stack = []
        self.context_namespace = None
        self.search_namespaces = None
        self._python_context = {}
        self.that = None


    def compile(self, tree):
        """
        Compile the parse tree into an executable plan
        :param tree: The parse tree
        :type tree: normParser.ModuleContext
        :return:
        """
        return

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

    def _push(self, node):
        self.stack.append(node)

    def _pop(self):
        return self.stack.pop()

    def _peek(self):
        return self.stack[-1] if len(self.stack) > 0 else None

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
        exe = None
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
        if exe is not None and isinstance(exe, NormExecutable):
            self.that = exe.lam
        return results

    def exitFull_statement(self, ctx:normParser.Full_statementContext):
        if ctx.comments() and ctx.statement():
            ne = self._peek()
            ne.add_description(ctx.comments())

    def exitStatement(self, ctx: normParser.StatementContext):
        if ctx.typeDeclaration() or ctx.typeDefinition() or ctx.typeImport() or ctx.typeExport():
            ne = self._peek()
            ne.atomic = ctx.ATOMIC() is not None

    def exitValidName(self, ctx:normParser.ValidNameContext):
        pass

    def exitQualifiedName(self, ctx:normParser.QualifiedNameContext):
        if ctx.DOT():
            valid_name = self._pop()
            qualified_name: QualifiedName = self._peek()
            qualified_name.add_attribute(valid_name)
        elif ctx.UUID():
            qualified_name = self._peek()
            qualified_name.add_version(ctx.UUID())
        else:
            self._push(QualifiedName(ctx.validName()))

    def exitType_(self, ctx:normParser.Type_Context):
        if ctx.LSBR():
            type_: Type = self._peek()
            type_.higher()
        else:
            qualified_name = self._pop()
            self._push(Type(qualified_name))

    def exitVariable(self, ctx:normParser.VariableContext):
        if ctx.FORMATTED():
            self._push(PivotVariable(ctx.FORMATTED()))
        elif ctx.FORMATTEDRAW():
            self._push(PivotVariable(ctx.FORMATTEDRAW()))
        else:
            self._push(Variable(ctx.getText()))

    def exitNames(self, ctx:normParser.NamesContext):
        qn = None
        vn = None
        names = []
        for ch in reversed(ctx.children):
            if isinstance(ch, normParser.QualifiedNameContext):
                qn = self._pop()
            elif isinstance(ch, normParser.VariableContext):
                vn = self._pop()
            elif isinstance(ch, normParser.COMMA):
                names.append((qn, vn))
                qn = None
                vn = None
        names.append((qn, vn))
        self._push(Names(list(reversed(names))))

    def exitTypeImport(self, ctx:normParser.TypeImportContext):
        names = self._pop()
        qn = None
        if ctx.qualifiedName():
            qn = self._pop()
        if isinstance(names, QualifiedName):
            tmp = names
            names = qn
            qn = tmp
        self._push(ImportNames(names, qn))

    def exitTypeExport(self, ctx:normParser.TypeExportContext):
        names = self._pop()
        qn = None
        if ctx.qualifiedName():
            qn = self._pop()
        if isinstance(names, QualifiedName):
            tmp = names
            names = qn
            qn = tmp
        self._push(ExportNames(names, qn))

    def exitVariableDeclaration(self, ctx:normParser.VariableDeclarationContext):
        if ctx.IS():

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
            expr: NormExpression = self._pop()
            self.scopes.append((QuantifiedLambda(expr), 'one_line_context'))
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
