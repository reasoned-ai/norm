from norm.compiler import NormCompiler
from norm.executable import NormExecutable
from norm.executable.expression.constant import Constant, MeasurementConstant
from norm.parser.normParser import normParser
from norm.models import norma
from typing import Optional


def remove_quotes(s: str):
    return s.strip("'")


def compile_constant_expr(compiler: NormCompiler,
                          constant_expr: normParser.ConstantContext
                          ) -> Optional[NormExecutable]:
    if constant_expr.BOOLEAN():
        return Constant(compiler, norma['native.Boolean'], bool(constant_expr.getText()))
    elif constant_expr.NONE():
        return Constant(compiler, norma['native.Any'], None)
    elif constant_expr.string():
        return Constant(compiler, norma['native.String'], remove_quotes(constant_expr.getText()))
    elif constant_expr.scalar():
        s: normParser.ScalarContext = constant_expr.scalar()
        if s.measurement():
            m: normParser.MeasurementContext = s.measurement()
            if m.INTEGER():
                value = int(m.INTEGER().getText())
                if m.NAME():
                    unit = m.NAME().getText()
                else:
                    unit = m.UNICODE_NAME().getText()
                return MeasurementConstant(compiler, norma['native.Integer'], value, unit)
            else:
                value = float(m.FLOAT().getText())
                if m.NAME():
                    unit = m.NAME().getText()
                else:
                    unit = m.UNICODE_NAME().getText()
                return MeasurementConstant(compiler, norma['native.Float'], value, unit)
        elif s.INTEGER():
            return Constant(compiler, norma['native.Integer'], int(s.INTEGER().getText()))
        else:
            return Constant(compiler, norma['native.Float'], float(s.FLOAT().getText()))
