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

unquoteVariable
    : variableName? LCBR variable RCBR
    ( variableName? LCBR variable RCBR )*
    ;

variableName: VARNAME | COMMAND | PROPERTY;

version: UUID | LATEST | BEST;

variable
    : variableName version?
    | variableName DOT variable
    | unquoteVariable
    ;

property: PROPERTY ( LBR constant RBR )?;

declaration
    : variableName? COLON ( variable | LSBR variable RSBR )
                  ( COLON property )?
    ;

declarationExpr
    : declaration ( COMMA declaration )*
    | variableName LBR declaration ( COMMA declaration )* RBR
    ;

projection
    : '?' variable?
    | '?' LBR variable ( COMMA variable )* RBR
    ;

code: ~( PYTHON_BLOCK | BLOCK_END )*;

codeExpr: PYTHON_BLOCK code BLOCK_END;

argumentExpr
    : variable? projection
    | ( variable IS )? arithmeticExpr projection?
    | variable conditionalRelation arithmeticExpr projection?
    ;

argumentExprs
    : LBR RBR
    | LBR argumentExpr ( COMMA argumentExpr )* RBR
    ;

evaluationExpr
    : constant
    | codeExpr
    | variable
    | variable argumentExprs
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

implementationExpr: variable IMPL expr;

rangedVariable: variable ( IN expr )?;

scope
    : WITH rangedVariable
    | FORANY rangedVariable
    | EXIST rangedVariable
    ;

scopes: scope COMMA ( scope COMMA )*;

scopedExpr: scopes expr;

expr
    : conditionExpr
    | declarationExpr
    | implementationExpr
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
    | uuid
    | datetime
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

logicalRelation: AND | OR | XOR | IMP | EQV;

conditionalRelation: EQ | NE | IN | NI | LT | LE | GT | GE | LK;

EXIST: E X I S T;
WITH: W I T H | W R T;
FORANY: F O R ( A L L | E A C H | A N Y | E V E R Y )?;

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

IMPL: IS | OR IS | AND IS;

SINGLELINE: '//' ~[\r\n]* [\r\n]* -> channel(HIDDEN);
MULTILINE: '/*' (.)*? '*/' [\r\n]* -> channel(HIDDEN);

WS: [ \t\u000C\u000B\r\n]+ -> channel(HIDDEN);

LBR: '(';
RBR: ')';

LCBR: '{';
RCBR: '}';

LSBR: '[';
RSBR: ']';

NONE:      N O N E | N U L L | N A;
IS:        I S | '=';
COLON:     ':';
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

BOOLEAN:    T R U E | F A L S E;
INTEGER:    [-]? DIGIT+;
FLOAT:      [-]? DIGIT+ DOT DIGIT+ ('e' [+-]? DIGIT+)?;
STRING:     '"' ( ~["\r\n\t] )*? '"' | '\'' ( ~['\r\n\t] )*? '\'' ;

UUID:      '$' [0-9a-zA-Z-]*;
DATETIME:  't' STRING;
LATEST:    '$' L A T E S T;
BEST:      '$' B E S T;

PYTHON_BLOCK : '{{';
BLOCK_END : '}}';

VARNAME: [a-zA-Z_][a-zA-Z0-9_]*;


fragment DIGIT:      [0] | NONZERO;
fragment NONZERO:    [1-9];

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
