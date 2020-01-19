import re
from enum import Enum
from typing import List
from norm.models.norm import Lambda
from norm.models.variable import Parameter, Input, Output, Parent
from norm.compiler import NormCompilable
from norm.compiler.exception import error_on, same
from norm.grammar.normParser import normParser
from norm.compiler.parsing import parse_type, parse_constant, parse_lambda, parse_type_name_version_module, \
    parse_comments

import logging
logger = logging.getLogger(__name__)


class TypeCategory(Enum):
    REGULAR = 0
    UNARY = 1
    BINARY = 2


PROP_ASC = 'asc'
PROP_DESC = 'desc'
PROP_PARAMETER = 'parameter'
PROP_TIME = 'time'
PROP_OID = 'oid'
PROP_PRIMARY = 'primary'
PROP_OPTIONAL = 'optional'


def _asc(properties):
    if PROP_ASC in properties:
        asc = True
        error_on(PROP_DESC in properties, 'Can not have both asc and desc for the same variable')
    elif PROP_DESC in properties:
        asc = False
        error_on(PROP_ASC in properties, 'Can not have both asc and desc for the same variable')
    else:
        asc = None
    return asc


class TypeDeclaration(NormCompilable):

    def _parse_output_declaration(self, output_declaration: normParser.OutputDeclarationContext):
        variables = []
        ch: normParser.VariableDeclarationContext
        for ch in output_declaration.getTypedRuleContexts(normParser.VariableDeclarationContext):
            error_on(ch.IS(), 'Output variable does not have default value')

            # get variable type and level
            type_: normParser.Type_Context = ch.type_()
            error_on(not type_, 'Output variable must have type')
            variable_type, type_level = parse_type(type_, self.compiler)

            # get variable property / category
            valid_names: List[str] = [vn.getText().lower() for vn in
                                      ch.getTypedRuleContexts(normParser.ValidNameContext)]
            variable_name = valid_names[0]

            properties = set(valid_names)

            # create variable
            v = Output(variable_type, variable_name, asc=_asc(properties), level=type_level,
                       as_primary=PROP_OPTIONAL not in properties)
            self.compiler.session.add(v)
            variables.append(v)

        t: normParser.Type_Context
        for t in output_declaration.getTypedRuleContexts(normParser.Type_Context):
            variable_type, type_level = parse_type(t, self.compiler)
            v = Output(variable_type, level=type_level)
            self.compiler.session.add(v)
            variables.append(v)

        return variables

    def _parse_input_declaration(self, input_declaration: normParser.InputDeclarationContext):
        variables = []
        ch: normParser.VariableDeclarationContext
        for ch in input_declaration.getTypedRuleContexts(normParser.VariableDeclarationContext):
            # get default value
            default_value = None
            default_type = None
            default_type_level = 0
            if ch.IS():
                default_value, default_type, default_type_level = parse_constant(ch.constant(), self.compiler)
                ch: normParser.VariableDeclarationContext = ch.variableDeclaration()
                error_on(ch.IS(), 'Only one time default value assignment allowed, but multiple detected.')

            # get variable type and level
            type_: normParser.Type_Context = ch.type_()
            if type_:
                variable_type, type_level = parse_type(type_, self.compiler)
                # TODO: check compatibility of default type and variable type
            else:
                variable_type = default_type
                type_level = default_type_level

            # get variable property / category
            valid_names: List[str] = [vn.getText().lower() for vn in
                                      ch.getTypedRuleContexts(normParser.ValidNameContext)]
            variable_name = valid_names[0]

            properties = set(valid_names)

            # create variable
            if PROP_PARAMETER in properties:
                v = Parameter(variable_type, variable_name, default_value, _asc(properties), type_level)
            else:
                v = Input(variable_type, variable_name, default_value, _asc(properties), type_level,
                          PROP_OPTIONAL not in properties, PROP_OID in properties, PROP_TIME in properties)
            self.compiler.session.add(v)
            variables.append(v)
        return variables

    def _parse_inheritance_declaration(self, inheritance: normParser.InheritanceDeclarationContext):
        variables = []
        ch: normParser.Type_Context
        for ch in inheritance.getTypedRuleContexts(normParser.Type_Context):
            v = Parent(type_=parse_lambda(ch.qualifiedName(), self.compiler))
            self.compiler.session.add(v)
            variables.append(v)
        return variables

    def compile(self, atomic, type_declaration, comments):
        """
        :type atomic: bool
        :type type_declaration: normParser.TypeDeclarationContext
        :type comments: str
        :rtype: List[NormExecutable]
        """
        type_version: str = ''
        type_operator: TypeCategory = TypeCategory.REGULAR
        if type_declaration.UNARY():
            type_name = type_declaration.STRING().getText()
            type_operator = TypeCategory.UNARY
        elif type_declaration.BINARY():
            type_name = type_declaration.STRING().getText()
            type_operator = TypeCategory.BINARY
        else:
            module_name, type_name, type_version = parse_type_name_version_module(type_declaration.qualifiedName())
            error_on(module_name,
                     f'Type declaration does not allow submodule to be created.\n'
                     f'Suggestion: remove {module_name}')

        # type inheritance
        inheritance: normParser.InheritanceDeclarationContext = type_declaration.inheritanceDeclaration()
        if inheritance:
            error_on(type_operator != TypeCategory.REGULAR,
                     'Operator does not have inheritance')
            inherited_types = self._parse_inheritance_declaration(type_declaration.inheritanceDeclaration())
        else:
            inherited_types = []

        # input declaration
        input_declaration: normParser.InputDeclarationContext = type_declaration.inputDeclaration()
        if input_declaration:
            declared_inputs = self._parse_input_declaration(input_declaration)
            error_on(type_operator == TypeCategory.UNARY and len(declared_inputs) != 1,
                     'Unary operator must have one input declaration')
            error_on(type_operator == TypeCategory.BINARY and len(declared_inputs) != 2,
                     'Binary operator must have two input declarations')
            error_on(type_operator == TypeCategory.BINARY and not same([inp.type_ for inp in declared_inputs]),
                     'Binary operator must have the same type for inputs')
        else:
            declared_inputs = []

        # output declaration
        output_declaration: normParser.OutputDeclarationContext = type_declaration.outputDeclaration()
        if output_declaration:
            declared_outputs = self._parse_output_declaration(output_declaration)
            error_on(type_operator != TypeCategory.REGULAR,
                     'Operator does not specify output type which is inferred instead')
        else:
            declared_outputs = []

        # description
        description = parse_comments(type_name, comments)

        # create or modify type
        bindings = inherited_types + declared_inputs + declared_outputs
        if type_version:
            t = self.get_lambda(self.compiler.current_module, type_name, type_version)
            error_on(not same(t.declared_bindings, bindings) and len(bindings) > 0,
                     'Declared variables are not the same as recorded.\n'
                     'Suggestions: remove the specified version to allow system to create a new version.')
            # append descriptions
            t.description += '\n' + description + '\n'
            # change the atomicity
            t.atomic = atomic
        else:
            t = Lambda(self.compiler.current_module, type_name, description, type_version, atomic, bindings)
            self.compiler.session.add(t)

        self.lam = t
        return []
