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
    : statement SEMICOLON
    ( statement SEMICOLON )* EOF;

statement
    : command
    | expr
    ;

command: COMMAND expr;

validName: NAME | COMMAND | PROPERTY | THIS | THAT | UNICODE_NAME;

qualifiedName
    : validName
    | validName ( DOT qualifiedName )*
    ;

version: UUID | LATEST | BEST;

type
    : qualifiedName
    | qualifiedName version
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
    : PROPERTY
    | PROPERTY ( LBR constant RBR )
    ;

variableDeclaration
    : validName ISA ( type | LSBR type RSBR )  property*
    ;

inheritanceDeclaration
    : ISA type
    | ISA type type*
    ;

typeDeclaration
    : type LBR variableDeclaration ( COMMA variableDeclaration )* RBR
    | type inheritanceDeclaration LBR variableDeclaration ( COMMA variableDeclaration )* RBR
    | type inheritanceDeclaration
    ;

projection
    : QUERY
    | QUERY variable
    | QUERY LBR variable ( COMMA variable )* RBR
    ;

positionalArgumentExpr
    : projection
    | arithmeticExpr projection?
    ;

keywordArgumentExpr
    : validName projection
    | validName IS arithmeticExpr projection?
    ;

argumentExprs
    : LBR RBR
    | LBR positionalArgumentExpr ( COMMA positionalArgumentExpr )* RBR
    | LBR keywordArgumentExpr ( COMMA keywordArgumentExpr )* RBR
    | LBR positionalArgumentExpr ( COMMA positionalArgumentExpr )* COMMA
          keywordArgumentExpr ( COMMA keywordArgumentExpr )* RBR
    | argumentExprs projection
    ;

code: ~( PYTHON_BLOCK | BLOCK_END )*;

codeExpr: PYTHON_BLOCK code BLOCK_END;

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

typeDefinition
    : type DEF expr
    | type ORDEF expr
    | type ANDDEF expr
    ;

domain
    : constant
    | qualifiedName
    | qualifiedName IN expr
    | qualifiedName IS expr
    ;

quantifier
    : FORANY domain
    | EXIST domain
    ;

quantifiedExpr: quantifier ( COMMA quantifier )* COMMA expr;

expr
    : conditionExpr
    | variableDeclaration
    | typeDeclaration
    | inheritanceDeclaration
    | typeDefinition
    | quantifiedExpr
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
    | uuid
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
uuid:        UUID;
datetime:    DATETIME;
measurement: ( integer_c | float_c ) NAME;

logicalRelation: AND | OR | XOR | IMP | EQV;

conditionalRelation: EQ | NE | IN | NI | LT | LE | GT | GE | LK;

EXIST: E X I S T | E X I S T S;
FORANY: F O R ( A L L | E A C H | A N Y | E V E R Y )?;

THIS: T H I S;
THAT: T H A T;

COMMAND: HISTORY | UNDO | REDO | DELETE | DESCRIBE | FIT | ANCHOR;

HISTORY: H I S T O R Y;
UNDO: U N D O;
REDO: R E D O;
DELETE: D E L E T E;
ANCHOR: A N C H O R;
DESCRIBE: D E S C R I B E;
FIT: F I T;

PROPERTY:  OPTIONAL | PRIMARY | OID | TIME | PARAMETER | STATE | OUTPUT;

OUTPUT: O U T P U T;
OPTIONAL: O P T I O N A L;
PRIMARY: P R I M A R Y;
OID: O I D;
TIME: T I M E;
PARAMETER: P A R A M E T E R;
STATE: S T A T E;

SINGLELINE: '//' ~[\r\n]* [\r\n]* -> channel(HIDDEN);
MULTILINE: '/*' (.)*? '*/' [\r\n]* -> channel(HIDDEN);

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

DEF: IS ':';
ORDEF: OR ':';
ANDDEF: AND ':';

BOOLEAN:    T R U E | F A L S E;
INTEGER:    [-]? DIGIT+;
FLOAT:      [-]? DIGIT+ DOT DIGIT+ ('e' [+-]? DIGIT+)?;
STRING:     '"' ( ~["] )*? '"' | '\'' ( ~['] )*? '\'' ;

UUID:      '$' [0-9a-zA-Z-]*;
DATETIME:  't' STRING;
LATEST:    '$' L A T E S T;
BEST:      '$' B E S T;

PYTHON_BLOCK : '{{';
BLOCK_END : '}}';

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
