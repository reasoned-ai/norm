grammar norm;

module: full_statement ( EMPTYLINES full_statement )* EMPTYLINES*;

full_statement
    : comments
    | statement
    | comments statement
    ;

comments
    : SINGLELINE+
    | MULTILINE
    ;

statement
    : ATOMIC? typeImports
    | ATOMIC? typeExports
    | ATOMIC? typeDeclarations
    | ATOMIC? typeDefinition
    | compoundExpr
    ;

validName: NAME | UNICODE_NAME | ATOMIC | BINARY | UNARY;

qualifiedName
    : validName | STRING
    | qualifiedName DOT (validName | STRING)
    | qualifiedName UUID
    ;

type_
    : qualifiedName
    | LSBR type_ RSBR
    ;

variable
    : validName
    | FORMATTED
    | FORMATTEDRAW
    ;

names: qualifiedName (AS variable)? ( COMMA qualifiedName (AS variable)? )* COMMA?;

typeImport
    : IMPORT names (DOT TIMES)?
    | IMPORT (names | TIMES) FROM qualifiedName
    | FROM qualifiedName IMPORT (names | TIMES)
    ;

typeImports: typeImport+;

typeExport
    : EXPORT (names | TIMES)
    | EXPORT (names | TIMES) TO qualifiedName
    | TO qualifiedName EXPORT (names | TIMES)
    ;

typeExports: typeExport+;

variableDeclaration
    : validName COLON type_ validName*
    | variableDeclaration IS constant
    ;

inputDeclaration
    : type_
    | variableDeclaration
    | LBR variableDeclaration ( COMMA variableDeclaration )* COMMA? RBR
    ;

outputDeclaration
    : MAPTO (variableDeclaration | type_)
    | MAPTO LBR variableDeclaration ( COMMA variableDeclaration )* COMMA? RBR
    ;

typeDeclaration
    : qualifiedName SUBT inputDeclaration* outputDeclaration*
    | ( UNARY | BINARY ) type_ STRING
    ;

typeDeclarations: typeDeclaration+;

typeDefinition
    : type_ definitionOperator compoundExpr
    | typeDeclaration definitionOperator compoundExpr
    ;

argumentExpr
    : simpleExpr
    | validName IS simpleExpr
    | argumentExpr QUERY
    ;

argumentExprs: LBR argumentExpr ( COMMA argumentExpr )* COMMA? RBR;

queryExpr
    : type_ ( LBR RBR )? QUERY?
    | type_ argumentExprs QUERY?
    ;

rangeExpr: scalar? COLON ( scalar ( COLON scalar )? )?;

evaluationExpr
    : constant
    | validName
    | rangeExpr
    | queryExpr
    | evaluationExpr LSBR simpleExpr RSBR
    | evaluationExpr DOT evaluationExpr
    ;

arithmeticExpr
    : evaluationExpr
    | LBR arithmeticExpr RBR
    | MINUS arithmeticExpr
    | arithmeticExpr EXP  arithmeticExpr
    | arithmeticExpr MOD arithmeticExpr
    | arithmeticExpr ( TIMES | DIVIDE ) arithmeticExpr
    | arithmeticExpr ( PLUS | MINUS ) arithmeticExpr
    ;

simpleExpr
    : arithmeticExpr
    | arithmeticExpr comparisonOperator arithmeticExpr
    ;

codeExpr
    : LCBR ~('\r\n')* RCBR
    | CODE_BLOCK_BEGIN ~( CODE_BLOCK_BEGIN | CODE_BLOCK_END )* CODE_BLOCK_END
    ;

returnExpr
    : RETURN simpleExpr ( (COMMA|MAPTO) simpleExpr )*
    | RETURN variable IS simpleExpr ( (COMMA|MAPTO) variable IS simpleExpr )*
    | RETURN simpleExpr AS variable ( (COMMA|MAPTO) simpleExpr AS variable )*;

compoundExpr
    : simpleExpr
    | codeExpr
    | returnExpr
    | WITH simpleExpr COLON compoundExpr
    | quantifier names IN simpleExpr COLON compoundExpr
    | variable ( COMMA variable )* DRAW compoundExpr
    | variable ( COMMA variable )* IS compoundExpr
    | compoundExpr AS variable ( COMMA variable )*
    | LBR compoundExpr RBR
    | NOT compoundExpr
    | compoundExpr complexLogicalOperator compoundExpr
    | compoundExpr simpleLogicalOperator compoundExpr
    ;

constant
    : NONE
    | BOOLEAN
    | string
    | scalar
    | constant ( COMMA constant )+ COMMA?
    | LBR constant ( COMMA constant )* COMMA? RBR
    | LSBR constant ( COMMA constant )* COMMA? RSBR
    | constant MAPTO constant
    ;

measurement: ( INTEGER | FLOAT ) ( NAME | UNICODE_NAME );

scalar: INTEGER | FLOAT | DATETIME | UUID | measurement;

string: STRING | RAW | FORMATTED | FORMATTEDRAW;

definitionOperator
    : DEF
    | ANDDEF
    | ORDEF
    | RDEF
    ;

simpleLogicalOperator: AND | OR | XOR | OTW;

complexLogicalOperator: IMP | EPT;

comparisonOperator: EQ | NE | IN | NI | LT | LE | GT | GE | LK | NK;

quantifier: EXIST | NEXIST | FORANY;

EXIST: E X I S T | E X I S T S;
NEXIST: N O T [ \t]* ( E X I S T | E X I S T S );
FORANY: F O R [ \t]* ( A L L | E A C H | A N Y | E V E R Y )?;

WITH: W I T H;

IMPORT: I M P O R T;
EXPORT: E X P O R T;
TO: T O;
FROM: F R O M;
AS: A S;

SINGLELINE: '#' ~[\r\n]*;
MULTILINE: ( '"""' | '\'\'\'')  [\r\n]+ (.)*? ( '"""' | '\'\'\'');

RETURN: R E T U R N;

ATOMIC: A T O M I C;
BINARY: B I N A R Y;
UNARY: U N A R Y;

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
DRAW:      '~';
IS:        '=';
QUERY:     '?';
COLON:     ':';
SUBT:      '::';
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
IMP:       '=>'  | I M P L Y;
EPT:       E X C E P T;
OTW:       O T H E R W I S E;

DEF: ':=';
RDEF: ':' INTEGER '=';
ORDEF: '|=';
ANDDEF: '&=';

BOOLEAN:   T R U E | F A L S E;
INTEGER:   [-]? DIGIT+;
FLOAT:     [-]? DIGIT+ DOT DIGIT+ ('e' [+-]? DIGIT+)?;
STRING:    '"' ( ~["] )*? '"' | '\'' ( ~['] )*? '\'' ;
RAW:       'r' STRING;
FORMATTED: 'f' STRING;
FORMATTEDRAW: ( 'fr' | 'rf' ) STRING;
DATETIME:  't' [0-9/-]+ ([ T] [0-9:]* ('.' [0-9]+)* ('-' [0-9:]+)*)* | 't' FLOAT;
UUID:   '$' [0-9a-zA-Z-]*;

CODE_BLOCK_BEGIN: SQL_BEGIN | PYTHON_BEGIN;
CODE_BLOCK_END: SQL_END | PYTHON_END;

SQL_BEGIN: '{sql';
SQL_END: 'sql}';

PYTHON_BEGIN: '{python' | '{py';
PYTHON_END: 'python}' | 'py}';

NAME: CHAR CHARDIGIT*;
UNICODE_NAME
    : [\p{Alpha}\p{General_Category=Other_Letter}] [\p{Alnum}\p{General_Category=Other_Letter}]*
    | COMMON_UNICODE+
    ;

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
