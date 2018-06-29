Grammar
====================================

.. productionlist::

    program
        : statement (WSS* statement)* WSS*
        ;

    statement
        : COMMENT
        | namespace WSS* ';'
        | using WSS* ';'
        | WSS* typeDeclaration WSS* ';'
        | WSS* expression WSS* ';'
        ;

    COMMENT
        : '//' ~[\r\n]* -> skip
        ;

    comments
        : '/*' code '*/'
        ;

    namespace
        : SPACED_NAMESPACE VARNAME ('.' VARNAME)*
        ;

    SPACED_NAMESPACE
        : 'namespace' [ \t]*
        ;

    using
        : SPACED_USING VARNAME ('.' VARNAME)*
        ;

    SPACED_USING
        : 'using' [ \t]*
        ;


    typeDeclaration
        :
        | anonymousTypeDeclaration
        | defaultTypeDeclaration
        | fullTypeDeclaration
        | incrementalTypeDeclaration
        ;

    anonymousTypeDeclaration
        : LCBR expression RCBR
        | LBR  RBR CL typeExpression AS typeImplementation
        | LBR argumentDeclarations RBR (CL typeExpression)* AS typeImplementation
        ;

    defaultTypeDeclaration
        : typeName LBR RBR CL typeExpression
        | typeName LBR argumentDeclarations RBR (CL typeExpression)*
        ;

    fullTypeDeclaration : defaultTypeDeclaration AS typeImplementation;

    incrementalTypeDeclaration
        : typeName ORIC typeImplementation
        | typeName ANDIC typeImplementation
        ;

    ORIC : [ \t\u000C]* OR '=' [ \t\u000C\r\n]*;
    ANDIC : [ \t\u000C]* AND '=' [ \t\u000C\r\n]*;

    argumentDeclaration
        : typeExpression
        | variableName CL typeExpression
        ;

    argumentDeclarations : argumentDeclaration (CA argumentDeclaration)*;

    version
        : '@' INTEGER
        | '@' INTEGER '.' uuid
        ;

    typeName : TYPENAME | TYPENAME version;
    variableName : VARNAME;

    typeExpression
        : typeName
        | typeName LCBR argumentExpressions RCBR
        ;

    typeEvaluation
        : typeExpression LBR RBR
        | typeExpression LBR argumentExpressions RBR
        | typeExpression LBR argumentExpressions RBR queryTerm
        | variableName LBR RBR
        | variableName LBR argumentExpressions RBR
        | variableName LBR argumentExpressions RBR queryTerm
        ;

    queryTerm
        : '?'
        | '?' variableName
        | '?' queryLimit
        | '?' queryLimit variableName
        | '*'
        | '*' variableName
        ;

    queryLimit : INTEGER;

    queryConstraints
        : queryContraint (logicalOperator queryContraint)*
        | queryContraint (logicalOperator WSS queryContraint)*
        | queryContraint (WSS logicalOperator queryContraint)*
        | queryContraint (WSS logicalOperator WSS queryContraint)*
        ;

    queryContraint
        : variableName constraintOperator expression
        | variableName constraintOperator WSS expression
        | variableName WSS constraintOperator expression
        | variableName WSS constraintOperator WSS expression
        ;

    argumentExpressions : argumentExpression (CA argumentExpression)*;

    argumentExpression
        : variableName AS expression
        | expression
        | variableName AS queryTerm
        | queryTerm
        | queryConstraints
        | LBR queryConstraints RBR queryTerm
        ;

    expression
        : constant
        | variableName ('.' propertyAggregation)*
        | typeEvaluation ('.' propertyAggregation)*
        | embracedExpression ('.' propertyAggregation)*
        | listExpression
        | variableName AS expression
        | NOT expression
        | NOT WSS expression
        | expression WSS logicalOperator WSS expression
        | expression logicalOperator WSS expression
        | expression WSS logicalOperator expression
        | expression logicalOperator expression
        ;

    listExpression
        : ARRAY
        | LSBR expression (CA expression)* RSBR;

    embracedExpression : LBR expression RBR;

    typeImplementation
        : LCBR RCBR
        | expression
        | LCBR expression RCBR
        | kerasImplementation
        | pytorchImplementation
        | pythonImplementation
        ;

    kerasImplementation
        : '{%keras' code '%}'
        ;

    pytorchImplementation
        : '{%pytorch' code '%}'
        ;

    pythonImplementation
        : '{%python' code '%}'
        ;

    code
        : ~('%}')*?
        ;

    propertyAggregation : variableName | aggregationEvaluation;

    aggregationFunction : 'Max' | 'Min' | 'Ave' | 'Count' | 'Group' | 'Unique';

    aggregationEvaluation
        : aggregationFunction LBR RBR
        | aggregationFunction LBR aggregationArgumentExpressions RBR
        ;

    aggregationArgumentExpression
        : variableName AS constant
        | variableName AS variableName
        | variableName AS aggregationFunction
        ;

    aggregationArgumentExpressions
        : aggregationArgumentExpression (CA aggregationArgumentExpression)*
        ;

    constant
        : INTEGER
        | FLOAT
        | STRING
        | UNICODE
        | pattern
        | uuid
        | url
        | datetime
        | tensor
        ;

    WSS: [ \t\u000C\r\n]+;

    LBR: '(' [ \t\u000C\r\n]*;
    RBR: [ \t\u000C\r\n]* ')';

    LCBR: '{' [ \t\u000C\r\n]*;
    RCBR: [ \t\u000C\r\n]* '}';

    LSBR: '[' [ \t\u000C\r\n]*;
    RSBR: [ \t\u000C\r\n]* ']';

    CA: [ \t\u000C\r\n]* ',' [ \t\u000C\r\n]*;

    CL: [ \t\u000C\r\n]* ':' [ \t\u000C\r\n]*;

    AS: [ \t\u000C\r\n]* '=' [ \t\u000C\r\n]*;

    logicalOperator: AND | OR | XOR | IMP | EQV | NOT AND | NOT OR | NOT XOR | NOT IMP | NOT EQV;
    constraintOperator: EQ | NE | IN | NIN | LT | LE | GT | GE | LIKE;

    IN:        'in';
    NIN:       '!in';
    AND:       '&';
    BSLASH:    '\\';
    COLON:     ':';
    COMMA:     ',';
    DIVIDE:    '/';
    DOT:       '.';
    DOTDOT:    '..';
    EQ:        '==';
    FSLASH:    '/';
    GE:        '>=';
    GT:        '>';
    LE:        '<=';
    LROUND:    '(';
    LT:        '<';
    MINUS:     '-';
    MOD:       '%';
    NOT:       '!';
    NE:        '!=';
    OR:        '|';
    PLUS:      '+';
    RROUND:    ')';
    SEMICOLON: ';';
    SPACE:     ' ';
    LIKE:      '~';
    TIMES:     '*';
    XOR:       '^';
    IMP:       '=>';
    EQV:       '<=>';

    INTEGER:   DIGIT+;
    FLOAT:      DIGIT+ DOT DIGIT+;
    NEWLINE:    '\r'? '\n';
    STRING:     '"' ( ~["] )+? '"' | '\'' ( ~['] )+? '\'' ;
    UNICODE:    'u' STRING;
    pattern:    'r' STRING;
    uuid:       '$' STRING;
    url:        'l' STRING;
    datetime:   't' STRING;
    tensor:     'm' ARRAY;

    ARRAY: LSBR ITEMS RSBR;

    ITEMS: ITEM (CA ITEM)*;

    ITEM: ARRAY | INTEGER | FLOAT;

    fragment DIGIT:      [0] | NONZERO;
    fragment NONZERO:    [1-9];


    TYPENAME
        : [A-Z][a-zA-Z0-9]*
        ;

    VARNAME
        : [a-z][a-zA-Z0-9_]*
        ;

    // WS represents a whitespace, which is ignored entirely by skip.
    WS
        : [ \t\u000C\r\n]+ -> skip
        ;
