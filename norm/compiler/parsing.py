import re
from typing import Tuple, Optional

from norm.compiler import error_on, NormCompiler, CodeType
from norm.grammar.normParser import normParser
from norm.models.norm import Lambda


def parse_comments(name: str, comments: str) -> str:
    """
    Parse comments according to a handler
    """
    if comments is None:
        return ''

    m = re.match(rf'@{name}{{[^{{}}]*}}', comments)
    if m:
        return m.group(1)
    else:
        return ''


def parse_type_name_version_module(
            qualified_name: normParser.QualifiedNameContext
        ) -> Tuple[Optional[str], str, Optional[str]]:
    """
    Parse type name, version and module from a qualified name
    :param qualified_name: the qualified name
    :return: module full name, type name and type version
    """
    type_version: Optional[str] = None
    if qualified_name.UUID():
        type_version = qualified_name.UUID().getText()[1:]
        qualified_name = qualified_name.qualifiedName()

    error_on(qualified_name.UUID(), 'Type can be referred by only one version at a time, multiple versions detected')

    if qualified_name.DOT():
        if qualified_name.validName():
            type_name = qualified_name.validName().getText()
        else:
            type_name = qualified_name.STRING().getText().strip('"\'')
        module_name = qualified_name.qualifiedName().getText().replace('"\'', '')
        error_on(module_name.find('$') > -1,
                 f"Module has no version, but a version sign detected for {module_name}.")
        return module_name, type_name, type_version
    else:
        return None, qualified_name.getText().strip('"\''), type_version


def parse_type(type_: normParser.Type_Context, context: NormCompiler) -> Tuple[Lambda, int]:
    """
    Parse the type
    :param type_: the type to parse
    :param context: the compiler
    :return:  the type and the level
    """
    type_level = 0
    while type_.type_():
        type_level += 1
        type_ = type_.type_()
    type_variable = parse_lambda(type_.qualifiedName(), context)
    return type_variable, type_level


def parse_lambda(qualified_name: normParser.QualifiedNameContext, context: NormCompiler) -> Lambda:
    """
    Retrieve type from the database
    :param qualified_name: the qualified name for the type
    :param context: the compiler
    :return: the type
    """
    module_name, type_name, type_version = parse_type_name_version_module(qualified_name)
    lam: Lambda = context.get_lambda(type_name, type_version, module_name)
    if lam is None:
        lam = context.create_lambda(name=type_name, atomic=False, code_type=CodeType.NORM)
    return lam


def parse_constant(constant: normParser.ConstantContext, context: NormCompiler) -> Tuple[object, Lambda, int]:
    """
    Build constant
    :param constant: the constant definition
    :param context: the compiler
    :return: the constant, the norm type and the type level
    """
    raise NotImplementedError


