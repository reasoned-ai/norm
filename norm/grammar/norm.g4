grammar norm;

script: statement (WS|NS)? SEMICOLON ((WS|NS)* statement (WS|NS)? SEMICOLON)* (WS|NS)?;

statement
    : comments
    | comments? imports
    | comments? exports
    | comments? commands
    | comments? (WS|NS)? multiLineExpression
    | comments? (WS|NS)? typeName (WS|NS)? IMPL (WS|NS)? LBR argumentDeclarations RBR
    | comments? (WS|NS)? typeName (WS|NS)? IMPL (WS|NS)? LBR renames RBR
    | comments? (WS|NS)? typeName (WS|NS)? IMPL (WS|NS)? codeExpression
    | comments? (WS|NS)? typeDeclaration ((WS|NS)? IMPL (WS|NS)? multiLineExpression)?
    ;

IMPL: CEQ | OEQ | AEQ;
CEQ: ':=';
OEQ: '|=';
AEQ: '&=';

SINGLELINE: '//' ~[\r\n]* [\r\n]*;
MULTILINE: '/*' (.)*? '*/' [\r\n]*;

comments: MULTILINE | SINGLELINE (SINGLELINE)*;

exports
    : SPACED_EXPORT typeName
    | SPACED_EXPORT typeName (WS|NS)? VARNAME (DOT VARNAME)* ((WS|NS)? AS (WS|NS)? VARNAME)?
    ;

SPACED_EXPORT: EXPORT [ \t]*;
EXPORT: 'export'|'Export'|'EXPORT';

imports
    : SPACED_IMPORT VARNAME (DOT VARNAME)* DOT '*'
    | SPACED_IMPORT VARNAME (DOT VARNAME)* DOT typeName ((WS|NS)? AS (WS|NS)? VARNAME)?
    ;

SPACED_IMPORT: IMPORT [ \t]*;
IMPORT: 'import'|'Import'|'IMPORT';

commands: SPACED_COMMAND typeName;

SPACED_COMMAND: COMMAND [ \t]+;
fragment HISTORY: 'history'|'History'|'HISTORY';
fragment UNDO: 'undo'|'Undo'|'UNDO';
fragment REDO: 'redo'|'Redo'|'REDO';
fragment DELETE: 'del'|'Del'|'DEL';
fragment DESCRIBE: 'describe'|'Describe'|'DESCRIBE';

COMMAND: HISTORY|UNDO|REDO|DELETE|DESCRIBE;
ARGOPT:  'optional' | 'primary' | 'oid' | 'time'| 'parameter' | 'state';

context
    : WITH LBR typeName RBR
    | FORANY LBR (variable (WS? COMMA WS? variable)*) RBR
    | FOREACH LBR (variable (WS? COMMA WS? variable)*) RBR
    | EXIST LBR(variable (WS? COMMA WS? variable)*) RBR
    ;

contexts: context (WS? DOT WS? context)* WS? COMMA;

EXIST: 'exist' | 'Exist' | 'EXIST';

WITH: 'with' | 'With' | 'WITH';

FOREACH
    : 'foreach' | 'forevery'
    | 'Foreach' | 'Forevery'
    | 'FOREACH' | 'FOREVERY'
    ;

FORANY
    : 'forall' | 'forany'
    | 'Forall' | 'Forany'
    | 'FORALL' | 'FORANY'
    ;

typeName
    : VARNAME version?
    | LSBR typeName RSBR;

unquote_variable
    : (VARNAME | COMMAND | ARGOPT)? LCBR variable RCBR ((VARNAME | COMMAND | ARGOPT | '_')? LCBR variable RCBR)*;

variable
    : VARNAME | COMMAND | ARGOPT
    | variable DOT variable
    | unquote_variable
    ;

argumentProperty: (WS|NS)? COLON (WS|NS)? ARGOPT WS? (LBR WS? constant WS? RBR)?;

argumentDeclaration : variable (WS|NS)? COLON (WS|NS)? typeName argumentProperty? | inheritance;

argumentDeclarations: argumentDeclaration ((WS|NS)? COMMA (WS|NS)? argumentDeclaration)*;

inheritanceArgument: arithmeticExpression | variable (WS|NS)? AS (WS|NS)? arithmeticExpression;

inheritanceArguments: inheritanceArgument ((WS|NS)? COMMA (WS|NS)? inheritanceArgument)*;

inheritance : typeName (WS|NS)? (LCBR inheritanceArguments RCBR)?;

rename: variable (WS|NS)? '->' (WS|NS)? variable;

renames: rename ((WS|NS)? COMMA (WS|NS)? rename)*;

typeDeclaration: typeName (LBR argumentDeclarations RBR)? ((WS|NS)? COLON (WS|NS)? typeName)?;

version: UUID | '$latest' | '$best';

queryProjection
    : '?' variable?
    | '?' LBR variable (WS? COMMA WS? variable)* RBR
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
    | LBR constant (WS? COMMA WS? constant)* RBR
    | LSBR constant (WS? COMMA WS? constant)* RSBR
    ;

code: ~(PYTHON_BLOCK|BLOCK_END)*;

codeExpression: PYTHON_BLOCK code BLOCK_END;

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
    | codeExpression
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
    : conditionExpression WS? queryProjection?
    | NOT WS? oneLineExpression
    | oneLineExpression spacedLogicalOperator oneLineExpression
    ;

contextualOneLineExpression
    : contexts? (WS|NS)? oneLineExpression;

multiLineExpression
    : contextualOneLineExpression
    | contextualOneLineExpression newlineLogicalOperator multiLineExpression
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

WS: [ \t\u000C]+;

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

IN:        'in'  | 'IN'  | 'In' ;
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
INTEGER:    [-]? DIGIT+;
FLOAT:      [-]? DIGIT+ DOT DIGIT+ ('e' [+-]? DIGIT+)?;
STRING:     '"' ( ~["\r\n\t] )*? '"' | '\'' ( ~['\r\n\t] )*? '\'' ;

PATTERN:   'p' STRING;
UUID:      '$' [0-9a-zA-Z-]*;
URL:       'u' STRING;
DATETIME:  't' STRING;

PYTHON_BLOCK : '{{' WS? [\r\n]?;
BLOCK_END : (WS|NS)? '}}';

VARNAME: [a-zA-Z][a-zA-Z0-9_]*;


fragment DIGIT:      [0] | NONZERO;
fragment NONZERO:    [1-9];


