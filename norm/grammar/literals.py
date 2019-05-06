from enum import Enum

import logging
logger = logging.getLogger(__name__)

OMMIT = '...'


class CodeMode(Enum):
    QUERY = ''
    PYTHON = '%python'
    KERAS = '%keras'
    SQL = '%sql'


class AOP(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    EXP = '**'

    def __str__(self):
        return self.value


class COP(Enum):
    GT = '>'
    GE = '>='
    LT = '<'
    LE = '<='
    EQ = '=='
    NE = '!='
    LK = '~'
    IN = 'in'
    NI = 'not in'

    def negate(self):
        if self is COP.GT:
            return COP.LE
        elif self is COP.GE:
            return COP.LT
        elif self is COP.LT:
            return COP.GE
        elif self is COP.LE:
            return COP.GT
        elif self is COP.EQ:
            return COP.NE
        elif self is COP.NE:
            return COP.EQ
        elif self is COP.IN:
            return COP.NI
        elif self is COP.NI:
            return COP.IN
        else:
            msg = 'Negated {} is not supported currently'.format(self)
            logger.error(msg)
            raise NotImplementedError(msg)

    def __str__(self):
        return self.value


class LOP(Enum):
    AND = 'and'
    OR = 'or'
    XOR = 'xor'
    NOT = 'not'
    IMP = 'imp'
    EQV = 'eqv'

    @classmethod
    def parse(cls, token):
        token = token.lower()
        if token == '!' or token == 'not':
            return cls.NOT
        elif token == '&' or token == 'and':
            return cls.AND
        elif token == '|' or token == 'or':
            return cls.OR
        elif token == '^' or token == 'xor':
            return cls.XOR
        elif token == '=>' or token == 'imp':
            return cls.IMP
        elif token == '<=>' or token == '<=>':
            return cls.EQV

    def negate(self):
        if self is LOP.AND:
            return LOP.OR
        elif self is LOP.OR:
            return LOP.AND
        else:
            msg = 'Negation only supports AND/OR for now'
            logger.error(msg)
            raise NotImplementedError(msg)

    def __str__(self):
        if self is LOP.XOR or self is LOP.IMP or self is LOP.EQV:
            msg = 'String representation only supports AND/OR/NOT for now'
            logger.error(msg)
            raise NotImplementedError(msg)
        return self.value


class MOP(Enum):
    HISTORY = 'history'
    DESCRIBE = 'describe'
    REDO = 'redo'
    UNDO = 'undo'
    DEL = 'del'


class ConstantType(Enum):
    NULL = 'none'
    BOOL = 'bool'
    INT = 'integer'
    FLT = 'float'
    STR = 'string'
    PTN = 'pattern'
    UID = 'uuid'
    URL = 'url'
    DTM = 'datetime'
    ANY = 'object'


class ImplType(Enum):
    DEF = ':='
    OR_DEF = '|='
    AND_DEF = '&='
