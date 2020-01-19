import re
from typing import Tuple, List
from norm.compiler.exception import error_on
from norm.grammar.normParser import normParser


def parse_comments(name, comments):
    """
    Parse comments according to a handler
    :type name: str
    :type comments: str
    :rtype: str
    """
    m = re.match(rf'@{name}{{[^{{}}]*}}', comments)
    if m:
        return m.group(1)
    else:
        return ''


def parse_type_name_version_module(qualified_name):
    """
    Parse type name, version and module from a qualified name
    :param qualified_name: the qualified name
    :type qualified_name: normParser.QualifiedNameContext
    :return: module, type name and type version
    :rtype: Tuple[str, str, str]
    """
    type_version = ''
    if qualified_name.UUID():
        type_version = qualified_name.UUID().getText()
        qualified_name = qualified_name.qualifiedName()

    error_on(qualified_name.UUID(), 'Type can be referred one version at a time, multiple versions detected')

    if qualified_name.DOT():
        return qualified_name.qualifiedName().getText(), qualified_name.validName().getText(), type_version
    else:
        return '', qualified_name.getText(), type_version


def parse_type(type_, context):
    """
    Parse the type
    :param type_: the type to parse
    :type type_: normParser.Type_Context
    :param context: the compiler
    :type context: norm.compiler.NormCompiler
    :return:  the type and the level
    :rtype: Tuple[norm.models.norm.Lambda, int]
    """
    type_level = 0
    while type_.type_():
        type_level += 1
        type_ = type_.type_()
    variable_type = parse_lambda(type_.qualifiedName(), context)
    return variable_type, type_level


def parse_variable(variable):
    """
    Parse the variable
    :type variable: normParser.VariableContext
    :rtype: norm.compiler.Variable
    """
    from norm.compiler import Variable
    if variable.validName():
        return Variable(variable.getText())
    else:
        return Variable(variable.getText(), pivot=True)


def parse_lambda(qualified_name, context):
    """
    Retrieve type from the database
    :param qualified_name: the qualified name for the type
    :type qualified_name: normParser.QualifiedNameContext
    :param context: the compiler
    :type context: norm.compiler.NormCompiler
    :return: the type
    :rtype: norm.models.norm.Lambda
    """
    raise NotImplementedError


def parse_constant(constant, context):
    """
    Build constant
    :param constant: the constant definition
    :type constant: normParser.ConstantContext
    :param context: the compiler
    :type context: norm.compiler.NormCompiler
    :return: the constant, the norm type and the type level
    :rtype: Tuple[object, norm.models.norm.Lambda, int]
    """
    raise NotImplementedError


