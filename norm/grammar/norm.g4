/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2019 by reasoned.ai
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 *
 */
grammar norm;

script
    : statement EMPTYLINE
    ( statement EMPTYLINE )* EOF;

statement
    : command
    | typeDeclaration
    | typeDefinition
    | typeExport
    | expr
    ;

command: COMMAND expr;

validName: NAME | COMMAND | VAR_PROPERTY | THIS | THAT | UNICODE_NAME;

typeExport
    : EXPORT type
    | EXPORT type TO qualifiedName
    | EXPORT type TO qualifiedName AS validName
    ;

qualifiedName
    : validName
    | validName ( DOT qualifiedName )*
    ;

type
    : qualifiedName
    | qualifiedName VERSION
    ;

listType
    : LSBR type RSBR
    ;

variable
    : qualifiedName
    | unquoteVariable
    ;

unquoteVariable
    : LCBR variable RCBR
    | qualifiedName LCBR variable RCBR
    | qualifiedName LCBR variable RCBR unquoteVariable*
    ;

property
    : VAR_PROPERTY
    | VAR_PROPERTY ( LBR constant RBR )
    ;

variableDeclaration
    : validName ISA ( type | listType )  property*
    | validName ISA property*
    ;

inheritanceDeclaration
    : INHERIT type type*
    ;

typeDeclaration
    : type LBR variableDeclaration ( COMMA variableDeclaration )* RBR
    | type inheritanceDeclaration LBR variableDeclaration ( COMMA variableDeclaration )* RBR
    | type inheritanceDeclaration
    ;

typeDefinition
    : typeDeclaration DEF expr
    | type DEF expr
    | type ORDEF expr
    | type ANDDEF expr
    | type RORDEF expr
    | type RANDDEF expr
    ;

projection
    : QUERY
    | QUERY INTEGER
    | QUERY variable
    | QUERY LBR variable ( COMMA variable )* RBR
    ;

positionalArgumentExpr
    : projection
    | expr projection?
    ;

keywordArgumentExpr
    : validName projection
    | validName IS expr projection?
    ;

argumentExprs
    : LBR RBR
    | LBR positionalArgumentExpr ( COMMA positionalArgumentExpr )* RBR
    | LBR keywordArgumentExpr ( COMMA keywordArgumentExpr )* RBR
    | LBR positionalArgumentExpr ( COMMA positionalArgumentExpr )* COMMA
          keywordArgumentExpr ( COMMA keywordArgumentExpr )* RBR
    | argumentExprs projection
    ;

code: ~( CODE_BLOCK_BEGIN | CODE_BLOCK_END )*;

codeExpr: CODE_BLOCK_BEGIN code CODE_BLOCK_END;

evaluationExpr
    : constant
    | codeExpr
    | variable
    | type
    | type argumentExprs
    | evaluationExpr LSBR integer_c? DOTDOT? integer_c? RSBR
    | evaluationExpr DOT evaluationExpr
    ;

arithmeticExpr
    : evaluationExpr
    | LBR arithmeticExpr RBR
    | MINUS arithmeticExpr
    | arithmeticExpr ( MOD | EXP ) arithmeticExpr
    | arithmeticExpr ( TIMES | DIVIDE ) arithmeticExpr
    | arithmeticExpr ( PLUS | MINUS ) arithmeticExpr
    ;

conditionExpr
    : arithmeticExpr
    | arithmeticExpr conditionalRelation arithmeticExpr
    ;

domainVariables : qualifiedName (COMMA qualifiedName)*;

domain
    : domainVariables
    | domainVariables IN expr
    | qualifiedName ISA type
    ;

quantifier
    : FORANY domain
    | EXIST domain
    ;

quantifiedExpr: quantifier ( COMMA quantifier )* COMMA expr;

scope
    : WITH type
    | WITH type AS validName
    | WITH validName FROM type
    ;

scopedExpr: scope COMMA expr;

expr
    : conditionExpr
    | variableDeclaration
    | inheritanceDeclaration
    | quantifiedExpr
    | scopedExpr
    | NOT expr
    | expr projection
    | LBR expr RBR
    | expr logicalRelation expr
    ;

constant
    : none
    | bool_c
    | integer_c
    | float_c
    | string_c
    | datetime
    | measurement
    | constant ( COMMA constant )+
    | LBR constant ( COMMA constant )* RBR
    | LSBR constant ( COMMA constant )* RSBR
    ;

none:        NONE;
bool_c:      BOOLEAN;
integer_c:   INTEGER;
float_c:     FLOAT;
string_c:    STRING;
datetime:    DATETIME;
measurement: ( integer_c | float_c ) NAME;

logicalRelation: AND | OR | XOR | IMP | EQV;

conditionalRelation: EQ | NE | IN | NI | LT | LE | GT | GE | LK | NK;

WITH: W I T H;
EXIST: E X I S T | E X I S T S;
FORANY: F O R ( A L L | E A C H | A N Y | E V E R Y )?;

THIS: T H I S;
THAT: T H A T;

TO: T O;
FROM: F R O M;
AS: A S;

COMMAND: HISTORY | UNDO | REDO | DELETE | DESCRIBE | FIT | ANCHOR;

HISTORY: H I S T O R Y;
UNDO: U N D O;
REDO: R E D O;
DELETE: D E L E T E;
ANCHOR: A N C H O R;
DESCRIBE: D E S C R I B E;
FIT: F I T;
EXPORT: E X P O R T;

VAR_PROPERTY:  OPTIONAL | PRIMARY | OID | TIME | PARAMETER | STATE | OUTPUT | DESC| ASC;

OUTPUT: O U T P U T;
OPTIONAL: O P T I O N A L;
PRIMARY: P R I M A R Y;
OID: O I D;
TIME: T I M E;
PARAMETER: P A R A M E T E R;
STATE: S T A T E;
DESC: D E S C;
ASC: A S C;

SINGLELINE: '//' ~[\r\n]* [\r\n]* -> channel(HIDDEN);
MULTILINE: '/*' (.)*? '*/' [\r\n]* -> channel(HIDDEN);

EMPTYLINE: [\r\n][\r\n]+;

WS: [ \t\u000B\u000C\r\n]+ -> channel(HIDDEN);

LBR: '(';
RBR: ')';

LCBR: '{';
RCBR: '}';

LSBR: '[';
RSBR: ']';

NONE:      N O N E | N U L L | N A;
IS:        I S | '=';
QUERY:     '?';
ISA:       I S A | ':';
INHERIT:   '::';
SEMICOLON: ';';
COMMA:     ',';
DOT:       '.';
DOTDOT:    '..';

IN:        I N;
NI:        '!' I N | N I N;
EQ:        '==' | E Q;
NE:        '!=' | N E Q;
GE:        '>=' | G E;
LE:        '<=' | L E;
GT:        '>' | G T;
LT:        '<' | L T;
LK:        '~' | L I K E;
NK:        '!~' | N L I K E;

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
IMP:       '=>'  | I M P;
EQV:       '<=>' | E Q V;

DEF: ':=';
ORDEF: OR '=';
ANDDEF: AND '=';
RORDEF: '||=';
RANDDEF: '&&=';

BOOLEAN:   T R U E | F A L S E;
INTEGER:   [-]? DIGIT+;
FLOAT:     [-]? DIGIT+ DOT DIGIT+ ('e' [+-]? DIGIT+)?;
STRING:    '"' ( ~["] )*? '"' | '\'' ( ~['] )*? '\'' ;
VERSION:   '$' [0-9a-zA-Z-]*;
DATETIME:  't' STRING;

CODE_BLOCK_BEGIN: '{{' | PYTHON_BEGIN;
CODE_BLOCK_END: '}}' | PYTHON_END;

PYTHON_BEGIN: '{python' | '{py';
PYTHON_END: 'python}' | 'py}';

NAME: CHAR CHARDIGIT*;
UNICODE_NAME : [\p{Alpha}\p{General_Category=Other_Letter}] [\p{Alnum}\p{General_Category=Other_Letter}]*;

fragment CHARDIGIT: CHAR | DIGIT;
fragment CHAR:    [a-zA-Z_];
fragment DIGIT:   [0] | NONZERO;
fragment NONZERO: [1-9];

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
