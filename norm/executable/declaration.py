from norm.executable import NormExecutable, NormError
from norm.executable.variable import VariableName
from norm.executable.type import TypeName
from norm.models import Lambda, Status
from typing import List

import logging
logger = logging.getLogger(__name__)


class ArgumentDeclaration(NormExecutable):

    def __init__(self, variable_name, variable_type):
        """
        The argument declaration
        :param variable_name: the name of the variable
        :type variable_name: VariableName
        :param variable_type: the type of the variable
        :type variable_type: TypeName
        """
        super().__init__()
        self.variable_name = variable_name
        self.variable_type = variable_type
        self.var = None

    def compile(self, context):
        session = context.session
        # TODO: jointly search the type for the variable
        lam = self.variable_type.lam
        if lam is None:
            msg = "Type {} for variable {} has not been declared yet"\
                .format(self.variable_type.name, self.variable_name)
            raise NormError(msg)

        from norm.models import Variable
        var = session.query(Variable).filter(Variable.name == self.variable_name.name,
                                             Variable.type_id == lam.id).scalar()
        if var is None:
            var = Variable(self.variable_name.name, lam)
            session.add(var)
        self.var = var
        return self

    def execute(self, context):
        raise NotImplementedError


class TypeDeclaration(NormExecutable):

    def __init__(self, type_name, argument_declarations, output_type_name):
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
        self.lam = None  # type: Lambda

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
        variables = [var_declaration.var for var_declaration in self.argument_declarations]
        lam = self.type_name.lam  # type: Lambda
        if lam is None:
            #  Create a new Lambda
            lam = Lambda(namespace=context.context_namespace, name=self.type_name.name)
            lam.description = self.description
            lam.variables = variables
            context.session.add(lam)
        else:
            assert(lam.status == Status.DRAFT)
            if sorted(lam.variables, key=lambda v: v.name) != sorted(variables, key=lambda v: v.name):
                # Revise the existing schema
                new_variables = {v.name: v.type_ for v in variables}
                current_variables = {v.name: v.type_ for v in lam.variables}
                lam.delete_variable([v.name for v in lam.variables if new_variables.get(v.name, None) != v.type_])
                lam.add_variable([v for v in variables if current_variables.get(v.name, None) != v.type_])
                # TODO: make a doc change revision
                if self.description:
                    lam.description = self.description
        self.lam = lam
        return self

    def execute(self, context):
        return self.lam

