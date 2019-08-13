from norm.executable import NormExecutable
from norm.executable.schema.variable import VariableName
from norm.executable.schema.type import TypeName
from norm.models import Lambda, Status, PythonLambda
from typing import List

import logging
logger = logging.getLogger(__name__)


class ArgumentDeclaration(object):

    def __init__(self, variable_name, variable_type, optional=False, as_oid=False, as_time=False):
        """
        The argument declaration
        :param variable_name: the name of the variable
        :type variable_name: VariableName
        :param variable_type: the type of the variable
        :type variable_type: TypeName
        :param optional: whether it is optional or not
        :type optional: bool
        :param as_time: whether it is a time column
        :type as_time: bool
        :param as_oid: whether is it an oid column
        :type as_oid: bool
        """
        assert(variable_type is not None)
        assert(variable_type.lam is not None)
        from norm.models import Variable
        self.var = Variable(variable_name.name, variable_type.lam, not optional, as_oid, as_time)


class RenameArgument(object):

    def __init__(self, variable_original_name, variable_new_name):
        """
        Rename a variable
        :param variable_original_name: the original name
        :type variable_original_name: str
        :param variable_new_name: the new name
        :type variable_new_name: str
        """
        self.variable_original_name = variable_original_name
        self.variable_new_name = variable_new_name


class TypeDeclaration(NormExecutable):

    def __init__(self, type_name, argument_declarations=None, output_type_name=None):
        """
        The type declaration
        :param type_name: the type name
        :type type_name: TypeName
        :param argument_declarations: the list of argument declarations
        :type argument_declarations: List[ArgumentDeclaration]
        :param output_type_name: the type_name as output, default to boolean
        :type output_type_name: TypeName
        """
        super().__init__()
        self.type_name = type_name
        self.argument_declarations = argument_declarations
        self.output_type_name = output_type_name
        self._description = None

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self.lam.description = value

    def compile(self, context):
        """
        Declare a type:
            * Create a type
            * Add new variable to a type # TODO
            * Modify description # TODO
            * Modify variables # TODO
        :return: the lambda
        :rtype: Lambda
        """
        # TODO: optimize to query db in batch for all types or utilize cache
        lam = self.type_name.lam  # type: Lambda
        if self.output_type_name is not None:
            output_arg = ArgumentDeclaration(VariableName(None, Lambda.VAR_OUTPUT), self.output_type_name)
            if self.argument_declarations is None:
                self.argument_declarations = [output_arg]
            else:
                self.argument_declarations.append(output_arg)
        if self.argument_declarations is None:
            variables = []
        else:
            variables = [var_declaration.var for var_declaration in self.argument_declarations]

        if lam is None or (len(variables) > 0 and sorted(lam.variables, key=lambda v: v.name)
                           != sorted(variables, key=lambda v: v.name)):
            #  Create a new Lambda
            lam = Lambda(namespace=context.context_namespace, name=self.type_name.name)
            lam.description = self.description
            lam.variables = variables
            context.session.add(lam)
            from norm.config import cache
            cache[(context.context_namespace, self.type_name.name, None, None)] = lam

        self.lam = lam
        return self


class AdditionalTypeDeclaration(TypeDeclaration):

    def __init__(self, type_name, argument_declarations):
        """
        Adding additional variables to the type or override the existing ones
        :param type_name: the name of type
        :type type_name: TypeName
        :param argument_declarations: the list of variables to add or modify
        :type argument_declarations: List[ArgumentDeclaration]
        """
        super().__init__(type_name, argument_declarations)

    def compile(self, context):
        lam = self.type_name.lam
        variables = [var_declaration.var for var_declaration in self.argument_declarations]
        assert(lam.status == Status.DRAFT)
        assert(sorted(lam.variables, key=lambda v: v.name) != sorted(variables, key=lambda v: v.name))
        # Revise the existing schema
        current_variables = {v.name: v.type_ for v in lam.variables}
        lam.add_variable([v for v in variables if v.name not in current_variables.keys()])
        lam.astype([v for v in variables if v.name in current_variables.keys()
                    and current_variables.get(v.name) != v.type_])
        self.lam = lam
        return self


class RenameTypeDeclaration(TypeDeclaration):

    def __init__(self, type_name, rename_arguments):
        """
        Rename the variables
        :param type_name: the name of the type
        :type type_name: TypeName
        :param rename_arguments: the list of variables to rename
        :type rename_arguments: List[RenameArgument]
        """
        super().__init__(type_name)
        self.rename_arguments = rename_arguments

    def compile(self, context):
        lam = self.type_name.lam
        assert(lam is not None)
        variables = {rename.variable_original_name: rename.variable_new_name for rename in self.rename_arguments
                     if rename.variable_original_name in lam}
        lam.rename_variable(variables)
        self.lam = lam
        return self


class CodeTypeDeclaration(TypeDeclaration):

    def __init__(self, type_name, code, description):
        """
        Declare a python lambda
        :param type_name: the name of the lambda
        :type type_name: TypeName
        :param code: the python code
        :type code: str
        :param description: the description of the lambda
        :type description: str
        """
        super().__init__(type_name)
        self.code = code
        self._description = description

    def compile(self, context):
        lam = PythonLambda(context.context_namespace, self.type_name.name, self.description, self.code)
        context.session.add(lam)
        from norm.config import cache
        cache[(context.context_namespace, self.type_name.name, None, None)] = lam
        self.lam = lam
        return self
