Grammar
====================================

.. productionlist::
    FunctionExpression : FunctionName "(" Arguments ")" [":=" DisjunctiveExpression]
                       : | FunctionName "(" Arguments ")" ["|:=" DisjunctiveExpression]
    Arguments : // empty
              : | Argument [, Arguments]
    Argument : FunctionName
             : FunctionExpression
             : VariableName ":" FunctionName
             : VariableName ":" "[" FunctionName "]"
             : VariableName ":" FunctionName "=" Expression
             : VariableName ":" "[" FunctionName "]" "=" "[" Expression "]"
             : VariableName "=" Expression
    Expression : None
               : VariableName
               : FunctionExpression
    DisjunctiveExpression : // empty
                          : | ConjunctiveExpression
                          : | "|" DisjunctiveExpression
                          : | "|" ConjunctiveExpression
                          : | "|" ConjunctiveExpression ";"
    ConjunctiveExpression : // empty
                          : | Expression
                          : | "&" ConjunctiveExpression
                          : | "&" Expression
                          : | "&" Expression ";"

