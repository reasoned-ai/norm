grammar norm;

script:
    | qualifiedName IS (  paragraph EMPTYLINES )+
    | qualifiedName IS (  paragraph EMPTYLINES )* paragraph
    ;


comments
    : SINGLELINE+
    | MULTILINE
    ;

paragraph:
    | comments? (relation COMMA comments?)+
    | comments? relation comments?
    | comments? (relation COMMA comments?)+ relation comments?
    ;

relation:
    | compoundExpr
    | externalCode
    | LBR paragraph RBR
    | LSBR paragraph RSBR
    | variables COLON relation
    | variables (COLON relation)? (ASSIGN | APPEND | OVERWRITE | DELETE) relation
    | MAPTO relation
    | OR relation
    | OR simpleExpr MAPTO relation
    | validName IS relation
    | quantifier variables (IN relation)? relation
    ;

expression:
    | constant
    | validName
    | validName UUID
    | validName DOT expression
    | LBR expression RBR
    | expression LBR paragraph RBR
    | expression LSBR number? COLON ( number ( COLON number )? )? RSBR
    ;

arithmeticExpr
    :
    | expression
    | LBR arithmeticExpr RBR
    | MINUS arithmeticExpr
    | arithmeticExpr EXP  arithmeticExpr
    | arithmeticExpr MOD arithmeticExpr
    | arithmeticExpr ( TIMES | DIVIDE ) arithmeticExpr
    | arithmeticExpr ( PLUS | MINUS ) arithmeticExpr
    ;

simpleExpr
    :
    | arithmeticExpr
    | arithmeticExpr comparisonOperator arithmeticExpr
    ;

compoundExpr
    :
    | simpleExpr
    | LBR compoundExpr RBR
    | NOT compoundExpr
    | compoundExpr ( AND | OR | XOR ) compoundExpr
    ;


validName: NAME | UNICODE_NAME;

qualifiedName
    : validName
    | qualifiedName DOT validName
    | qualifiedName UUID
    ;

variable
    :
    | validName ( LCBR relation RCBR )*
    ;

variables
    : variable ( COMMA variable )*
    ;

externalCode: CODE_BLOCK_BEGIN ~(CODE_BLOCK_BEGIN | CODE_BLOCK_END)* CODE_BLOCK_END;

constant
    : NONE
    | string
    | number
    | measurement
    ;

measurement: ( INTEGER | FLOAT ) validName;

number: BOOLEAN| INTEGER | FLOAT | DATETIME;

string: STRING | RAW | FORMATTED | FORMATTEDRAW;

comparisonOperator: EQ | NE | IN | NI | LT | LE | GT | GE | LK | NK;

quantifier: EXIST | NEXIST | FORANY;

EXIST: E X I S T | E X I S T S;
NEXIST: N O T [ \t]* ( E X I S T | E X I S T S );
FORANY: F O R [ \t]* ( A L L | E A C H | A N Y | E V E R Y )?;

AS: A S;

SINGLELINE: '#' ~[\r\n]*;
MULTILINE: ( '"""' | '\'\'\'')  [\r\n]+ (.)*? ( '"""' | '\'\'\'');

EMPTYLINES: [ \t]* [\r\n] ( [ \t]* [\r\n] )+ [ \t]*;

WS: [ \t\u000B\u000C\r\n]+ -> channel(HIDDEN);

LBR: '(';
RBR: ')';

LSBR: '[';
RSBR: ']';

LCBR: '{';
RCBR: '}';

MAPTO:     '->';

NONE:      N O N E | N U L L | N A;
ASSIGN:    '=';
APPEND:    '|=';
OVERWRITE: '&=';
DELETE:    '-=';
COLON:     ':';
SEMICOLON: ';';
IS:        '::';
COMMA:     ',';
DOT:       '.';

IN:        I N;
NI:        NOT [ \t]* IN;
EQ:        '==';
NE:        '!=';
GE:        '>=';
LE:        '<=';
GT:        '>';
LT:        '<';
LK:        L I K E;
NK:        U N L I K E | NOT [ \t]* LK;

MINUS:     '-';
PLUS:      '+';
TIMES:     '*';
DIVIDE:    '/';
EXP:       '**';
MOD:       '%';

NOT:       '!'   | N O T;
AND:       '&'   | A N D;
OR:        '|'   | O R;
XOR:       '^'   | X O R;

NAME: CHAR CHARDIGIT*;
UNICODE_NAME
    : [\p{Alpha}\p{General_Category=Other_Letter}] [\p{Alnum}\p{General_Category=Other_Letter}]*
    | COMMON_UNICODE+
    ;

BOOLEAN:   T R U E | F A L S E;
INTEGER:   [-]? DIGIT+;
FLOAT:     [-]? DIGIT+ DOT DIGIT+ ('e' [+-]? DIGIT+)?;
STRING:    '"' ( ~["] )*? '"' | '\'' ( ~['] )*? '\'' ;
RAW:       'r' STRING;
FORMATTED: 'f' STRING;
FORMATTEDRAW: ( 'fr' | 'rf' ) STRING;
DATETIME:  't' [0-9/-]+ ([ T] [0-9:]* ('.' [0-9]+)* ('-' [0-9:]+)*)* | 't' FLOAT;
UUID:   '$' [0-9a-zA-Z-]*;

CODE_BLOCK_BEGIN: '{{';
CODE_BLOCK_END: '}}';

fragment CHARDIGIT: CHAR | DIGIT;
fragment CHAR:    [a-zA-Z_];
fragment DIGIT:   [0] | NONZERO;
fragment NONZERO: [1-9];
fragment COMMON_UNICODE: '\u00a1'..'\ud7ff';


fragment A : [aA];
fragment B : [bB];
fragment C : [cC];
fragment D : [dD];
fragment E : [eE];
fragment F : [fF];
fragment G : [gG];
fragment H : [hH];
fragment I : [iI];
fragment J : [jJ];
fragment K : [kK];
fragment L : [lL];
fragment M : [mM];
fragment N : [nN];
fragment O : [oO];
fragment P : [pP];
fragment Q : [qQ];
fragment R : [rR];
fragment S : [sS];
fragment T : [tT];
fragment U : [uU];
fragment V : [vV];
fragment W : [wW];
fragment X : [xX];
fragment Y : [yY];
fragment Z : [zZ];
