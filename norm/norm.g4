grammar norm;

script: statement ((WS|NS)? statement)* (WS|NS)?;

statement
    : comments SEMICOLON
    | comments? imports (WS|NS)? SEMICOLON
    | comments? exports (WS|NS)? SEMICOLON
    | comments? (WS|NS)? typeDeclaration (WS|NS)? SEMICOLON
    | comments? typeName (WS|NS)? COLON EQ (WS|NS)? multiLineExpression (WS|NS)? SEMICOLON
    | comments? typeName (WS|NS)? OR EQ (WS|NS)? multiLineExpression (WS|NS)? SEMICOLON
    | comments? typeName (WS|NS)? AND EQ (WS|NS)? multiLineExpression (WS|NS)? SEMICOLON
    | comments? (WS|NS)? multiLineExpression (WS|NS)? SEMICOLON
    ;

SINGLELINE: '//' ~[\r\n]* [\r\n]*;
MULTILINE: '/*' (.)*? '*/' [\r\n]*;

comments: MULTILINE | SINGLELINE (SINGLELINE)*;

exports
    : SPACED_EXPORT typeName
    | SPACED_EXPORT typeName (WS|NS)? VARNAME (DOT VARNAME)* ((WS|NS)? AS (WS|NS)? VARNAME)?
    ;

SPACED_EXPORT: 'export'|'Export'|'EXPORT' [ \t]*;

imports
    : SPACED_IMPORT VARNAME (DOT VARNAME)* DOT '*'
    | SPACED_IMPORT VARNAME (DOT VARNAME)* DOT typeName ((WS|NS)? AS (WS|NS)? VARNAME)?
    ;

SPACED_IMPORT: 'import'|'Import'|'IMPORT' [ \t]*;

argumentDeclaration : variable (WS|NS)? COLON (WS|NS)? typeName;

argumentDeclarations: argumentDeclaration ((WS|NS)? COMMA (WS|NS)? argumentDeclaration)*;

typeDeclaration : typeName (LBR argumentDeclarations RBR)? ((WS|NS)? COLON (WS|NS)? typeName)?;

version: '@' INTEGER?;

typeName
    : VARNAME version?
    | LSBR typeName RSBR;

variable
    : VARNAME
    | variable DOT VARNAME
    ;

queryProjection
    : '?' variable?
    | '?' LCBR variable (COMMA variable)* RCBR
    | '?' LBR variable (COMMA variable)* RBR
    ;

constant
    : none
    | bool_c
    | integer_c
    | float_c
    | string_c
    | pattern
    | uuid
    | url
    | datetime
    | LSBR constant (COMMA constant)* RSBR
    ;

code: ~(PYTHON_BLOCK|SQL_BLOCK|BLOCK_END)*;

codeExpression: (PYTHON_BLOCK|SQL_BLOCK) code BLOCK_END;

argumentExpression
    : arithmeticExpression
    | queryProjection
    | variable queryProjection
    | variable (WS|NS)? AS (WS|NS)? arithmeticExpression queryProjection?
    | variable spacedConditionOperator arithmeticExpression queryProjection?
    ;

argumentExpressions
    : LBR RBR
    | LBR argumentExpression ((WS|NS)? COMMA (WS|NS)? argumentExpression)* RBR
    ;

evaluationExpression
    : constant
    | codeExpression
    | variable
    | argumentExpressions
    | variable argumentExpressions
    | evaluationExpression (WS|NS)? DOT (WS|NS)? evaluationExpression
    ;

slicedExpression
    : evaluationExpression
    | evaluationExpression LSBR integer_c? (WS|NS)? COLON? (WS|NS)? integer_c? RSBR
    | evaluationExpression LSBR evaluationExpression RSBR
    ;

arithmeticExpression
    : slicedExpression
    | LBR arithmeticExpression RBR
    | MINUS arithmeticExpression
    | arithmeticExpression (WS|NS)? (MOD | EXP) (WS|NS)? arithmeticExpression
    | arithmeticExpression (WS|NS)? (TIMES | DIVIDE) (WS|NS)? arithmeticExpression
    | arithmeticExpression (WS|NS)? (PLUS | MINUS) (WS|NS)? arithmeticExpression
    ;

conditionExpression
    : arithmeticExpression
    | arithmeticExpression spacedConditionOperator arithmeticExpression
    ;

oneLineExpression
    : conditionExpression queryProjection?
    | NOT WS? oneLineExpression
    | oneLineExpression spacedLogicalOperator oneLineExpression
    ;

multiLineExpression
    : oneLineExpression
    | oneLineExpression newlineLogicalOperator multiLineExpression
    ;


none:        NONE;
bool_c:      BOOLEAN;
integer_c:   INTEGER;
float_c:     FLOAT;
string_c:    STRING;
pattern:     PATTERN;
uuid:        UUID;
url:         URL;
datetime:    DATETIME;

logicalOperator: AND | OR | NOT | XOR | IMP | EQV;

spacedLogicalOperator: WS? logicalOperator WS?;

newlineLogicalOperator: NS logicalOperator WS?;

conditionOperator: EQ | NE | IN | NI | LT | LE | GT | GE | LK;

spacedConditionOperator: (WS|NS)? conditionOperator (WS|NS)?;

WS: [ \t\u000C]+ -> skip;

NS: [ \t\u000C]+ [\r\n] [ \t\u000C]* | [\r\n] [ \t\u000C]*;

LBR: '(' (WS|NS)?;
RBR: (WS|NS)? ')';

LCBR: '{' (WS|NS)?;
RCBR: (WS|NS)? '}';

LSBR: '[' (WS|NS)?;
RSBR: (WS|NS)? ']';

NONE:      'none' | 'null' | 'na' | 'None' | 'Null' | 'Na' | 'NONE' | 'NULL' | 'NA';
AS:        'as' | 'As' | 'AS' | '=';
COLON:     ':';
SEMICOLON: ';';
COMMA:     ',';
DOT:       '.';
DOTDOT:    '..';

IN:        'in'  | 'IN'  | 'In';
NI:        '!in' | '!IN' | '!In';
EQ:        '==';
NE:        '!=';
GE:        '>=';
LE:        '<=';
GT:        '>';
LT:        '<';
LK:        '~';

MINUS:     '-';
PLUS:      '+';
TIMES:     '*';
DIVIDE:    '/';
EXP:       '**';
MOD:       '%';

NOT:       '!'   | 'not' | 'Not' | 'NOT';
AND:       '&'   | 'and' | 'And' | 'AND';
OR:        '|'   | 'or'  | 'Or'  | 'OR';
XOR:       '^'   | 'xor' | 'Xor' | 'XOR';
IMP:       '=>'  | 'imp' | 'Imp' | 'IMP';
EQV:       '<=>' | 'eqv' | 'Eqv' | 'EQV';

BOOLEAN:    'true' | 'false' | 'True' | 'False' | 'TRUE' | 'FALSE';
INTEGER:    [+-]? DIGIT+;
FLOAT:      [+-]? DIGIT+ DOT DIGIT+ ('e' [+-]? DIGIT+)?;
STRING:     '"' ( ~["\r\n\t] )*? '"' | '\'' ( ~['\r\n\t] )*? '\'' ;

PATTERN:   'r' STRING;
UUID:      '$' STRING;
URL:       'u' STRING;
DATETIME:  't' STRING;

SHOW: '%show' (WS|NS)?;
DELETE: '%delete' (WS|NS)?;

PYTHON_BLOCK : '{%python' (WS|NS)?;
SQL_BLOCK : '{%sql' (WS|NS)?;
BLOCK_END : '%}';

VARNAME: [a-zA-Z][a-zA-Z0-9_]*;

fragment DIGIT:      [0] | NONZERO;
fragment NONZERO:    [1-9];


