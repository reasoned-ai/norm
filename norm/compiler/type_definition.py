from typing import List
from norm.compiler import NormCompilable
from norm.compiler.parsing import parse_type
from norm.grammar.normParser import normParser
from norm.models.norm import Lambda
from norm.compiler.type_declaration import TypeDeclaration


class TypeDefinition(NormCompilable):

    def compile(self, atomic, type_definition, comments):
        """
        :type atomic: bool
        :type type_definition: normParser.TypeDefinitionContext
        :type comments: str
        :rtype: List[NormExecutable]
        """
        variable_type: Lambda
        type_level: int
        type_declaration: normParser.TypeDeclarationContext = type_definition.typeDeclaration()
        if type_declaration:
            td = TypeDeclaration(self.compiler)
            td.compile(atomic, type_declaration, comments)
            variable_type = td.lam
        else:
            type_: normParser.Type_Context = type_definition.type_()
            variable_type, type_level = parse_type(type_, self.compiler)
        definition_operator: normParser.DefinitionOperatorContext = type_definition.definitionOperator()

        pass


