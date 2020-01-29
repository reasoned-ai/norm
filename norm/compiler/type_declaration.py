import logging
from typing import List

from norm.compiler import error_on, same
from norm.compiler.parsing import parse_type, parse_constant, parse_type_name_version_module, \
    parse_comments
from norm.compiler.type_definition import CodeType
from norm.grammar import *
from norm.grammar.normParser import normParser
from norm.models.variable import Parameter, Input, Output, Parent, Variable
from norm.utils import new_version, random_name

logger = logging.getLogger(__name__)


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


def _parse_output_declaration(compiler, output_declaration, group):
    """
    :type compiler: norm.compiler.NormCompiler
    :type output_declaration: normParser.OutputDeclarationContext
    :type group: int
    :rtype: List[Variable]
    """
    if output_declaration.type_():
        variable_type, type_level = parse_type(output_declaration.type_(), compiler)
        v = Output(variable_type, OUTPUT_VAR_STUB + random_name(), level=type_level, group=group)
        compiler.session.add(v)
        return [v]

    variables = []
    ch: normParser.VariableDeclarationContext
    for ch in output_declaration.getTypedRuleContexts(normParser.VariableDeclarationContext):
        error_on(ch.IS(), 'Output variable does not have default value')

        # get variable type and level
        type_: normParser.Type_Context = ch.type_()
        error_on(not type_, 'Output variable must have type')
        variable_type, type_level = parse_type(type_, compiler)

        # get variable property / category
        valid_names: List[str] = [vn.getText().lower() for vn in
                                  ch.getTypedRuleContexts(normParser.ValidNameContext)]
        variable_name = valid_names[0]

        properties = set(valid_names)

        # create variable
        v = Output(variable_type, variable_name, asc=_asc(properties), level=type_level,
                   as_primary=PROP_OPTIONAL not in properties, group=group)
        compiler.session.add(v)
        variables.append(v)

    return variables


def _parse_input_declaration(compiler, input_declaration):
    """
    :type compiler: norm.compiler.NormCompiler
    :type input_declaration: normParser.InputDeclarationContext
    :rtype: List[Variable]
    """
    variables = []
    ch: normParser.VariableDeclarationContext
    for ch in input_declaration.getTypedRuleContexts(normParser.VariableDeclarationContext):
        # get default value
        default_value = None
        default_type = None
        default_type_level = 0
        if ch.IS():
            default_value, default_type, default_type_level = parse_constant(ch.constant(), compiler)
            ch: normParser.VariableDeclarationContext = ch.variableDeclaration()
            error_on(ch.IS(), 'Only one time default value assignment allowed, but multiple detected.')

        # get variable type and level
        type_: normParser.Type_Context = ch.type_()
        if type_:
            type_variable, type_level = parse_type(type_, compiler)
            error_on(default_type_level != type_level,
                     f'Default value has different type level than provided type:'
                     f'default({default_type_level})!=given{type_level}')
            # TODO: check compatibility of default type and variable type
        else:
            type_variable = default_type
            type_level = default_type_level

        # get variable property / category
        valid_names: List[str] = [vn.getText().lower() for vn in
                                  ch.getTypedRuleContexts(normParser.ValidNameContext)]
        variable_name = valid_names[0]

        properties = set(valid_names)

        # create variable
        if PROP_PARAMETER in properties:
            v = Parameter(type_variable, variable_name, default_value, _asc(properties), type_level)
        else:
            v = Input(type_variable, variable_name, default_value, _asc(properties), type_level,
                      PROP_OPTIONAL not in properties, PROP_OID in properties, PROP_TIME in properties)
        compiler.session.add(v)
        variables.append(v)
    return variables


def _parse_inheritance_declaration(compiler, inheritance):
    """
    :type compiler: norm.compiler.NormCompiler
    :type inheritance: normParser.Type_Context
    :rtype: Variable
    """
    type_variable, type_level = parse_type(inheritance, compiler)
    error_on(type_level > 0,
             'Parametrized type or inherited type does not support higher order form.'
             'Suggestion: assign a variable of higher order type')
    v = Parent(type_=type_variable)
    compiler.session.add(v)
    return v


def _parse_unary_declaration(compiler, type_, name, comments):
    """
    :type compiler: norm.compiler.NormCompiler
    :type type_: normParser.Type_Context
    :type name: str
    :rtype: norm.models.norm.Lambda
    """
    description = parse_comments(name, comments)
    type_variable, type_level = parse_type(type_, compiler)
    from norm.models.native import UnaryOperator
    t = UnaryOperator(module=compiler.current_module, name=name, description=description, type_=type_variable,
                      type_level=type_level, version=new_version())
    compiler.session.add(t)
    compiler.current_scope = t
    return t


def _parse_binary_declaration(compiler, type_, name, comments):
    """
    :type compiler: norm.compiler.NormCompiler
    :type type_: normParser.Type_Context
    :type name: str
    :rtype: norm.models.norm.Lambda
    """
    description = parse_comments(name, comments)
    type_variable, type_level = parse_type(type_, compiler)
    from norm.models.native import BinaryOperator
    t = BinaryOperator(module=compiler.current_module, name=name, description=description, type_=type_variable,
                       type_level=type_level, version=new_version())
    compiler.session.add(t)
    compiler.current_scope = t
    return t


def compile_type_declaration(compiler, atomic, type_declaration, comments, code_type=CodeType.NORM):
    """
    :type compiler: norm.compiler.NormCompiler
    :type atomic: bool
    :type type_declaration: normParser.TypeDeclarationContext
    :type comments: str
    :type code_type: CodeType
    :rtype: norm.models.norm.Lambda
    """
    if type_declaration.UNARY():
        return _parse_unary_declaration(compiler,
                                        type_declaration.type_(),
                                        type_declaration.STRING().getText(),
                                        comments)

    if type_declaration.BINARY():
        return _parse_binary_declaration(compiler,
                                         type_declaration.type_(),
                                         type_declaration.STRING().getText(),
                                         comments)

    # Parse regular type
    module_name, type_name, type_version = parse_type_name_version_module(type_declaration.qualifiedName())
    error_on(module_name is not None,
             f'Type declaration does not allow submodule yet.\n'
             f'Suggestion: remove {module_name.getText()}')

    # input declaration
    declared_inputs = []
    inherited_types = []
    input_declarations = type_declaration.getTypedRuleContexts(normParser.InputDeclarationContext)
    if input_declarations:
        input_declaration: normParser.InputDeclarationContext
        for input_declaration in input_declarations:
            if input_declaration.type_():
                inherited_types.append(_parse_inheritance_declaration(compiler, input_declaration.type_()))
            else:
                declared_inputs.extend(_parse_input_declaration(compiler, input_declaration))

    # output declaration
    declared_outputs = []
    output_declarations = type_declaration.getTypedRuleContexts(normParser.OutputDeclarationContext)
    if output_declarations:
        for i, output_declaration in enumerate(output_declarations):
            declared_outputs.extend(_parse_output_declaration(compiler, output_declaration, i))

    error_on(not (declared_inputs or inherited_types or declared_outputs),
             'Declaration of a type is empty')

    # description
    description = parse_comments(type_name, comments)

    # create or modify type
    bindings = inherited_types + declared_inputs + declared_outputs
    if type_version:
        t = compiler.get_lambda(type_name, compiler.current_module, type_version)
        error_on(type_version != t.version,
                 f'Specified version {type_version} does not exist for type {type_name}.')
        error_on(not same(t.declared_bindings, bindings) and len(bindings) > 0,
                 'Declared variables are not the same as recorded.\n'
                 'Suggestions: remove the specified version to allow system to create a new version.')
        # append description
        t.description += '\n' + description + '\n'
        # change the atomicity
        t.atomic = atomic
    else:
        t = compiler.get_lambda(type_name,
                                module=compiler.current_module,
                                version=new_version(),
                                description=description,
                                atomic=atomic,
                                bindings=bindings,
                                code_type=code_type)
    compiler.current_scope = t
    return t
