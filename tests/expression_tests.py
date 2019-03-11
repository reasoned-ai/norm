"""Unit tests for Norm"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest
from textwrap import dedent
from norm import engine
import re
from dateutil import parser as dateparser


class ExpressionTestCase(unittest.TestCase):

    constant_tests = {
        "null;": ('none', None),
        "true;": ('bool', True),
        "false;": ('bool', False),
        "34;": ('int', 34),
        "34.343;": ('float', 34.343),
        "'';": ('string', ''),
        "'test';": ('string', 'test'),
        "u'test';": ('unicode', b'test'),
        "r'\W+';": ('pattern', re.compile('\W+')),
        "$'sfs2123';": ('uuid', 'sfs2123'),
        "l'http://example.com';": ('url', 'http://example.com'),
        "t'2018/08/12 23:34:01';": ('datetime', dateparser.parse('2018/08/12 23:34:01', fuzzy=True))
    }

    base_expression_tests = {
        "true;": ('constant', engine.Constant('bool', True)),
        "Test;": ('type', engine.TypeName('Test', None)),
        "test;": ('variable', 'test')
    }

    def test_recognize_constant(self):
        for s, (t, v) in self.constant_tests.items():
            exe = engine.compile_norm(s)
            cmd = exe.stack.pop()
            self.assertEqual(cmd.value.type_name, t)
            self.assertEqual(cmd.value.value, v)

    def test_recognize_base_expression(self):
        for s, (t, v) in self.base_expression_tests.items():
            exe = engine.compile_norm(s)
            cmd = exe.stack.pop()
            self.assertEqual(cmd.type_name, t)
            self.assertEqual(cmd.value, v)

    def test_recognize_list_expression(self):
        script = dedent("""
        [2.3, 1.1];
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.elements, [engine.BaseExpr('constant', engine.Constant('float', 2.3)),
                                        engine.BaseExpr('constant', engine.Constant('float', 1.1))])

    def test_evaluation_expression1(self):
        script = dedent("""
        Match(short_description, hr_service);
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.type_name, engine.TypeName('Match', None))
        self.assertEqual(cmd.args, engine.ListExpr(
            [engine.ArgumentExpr(engine.BaseExpr('variable', 'short_description'), None),
             engine.ArgumentExpr(engine.BaseExpr('variable', 'hr_service'), None)]))

    def test_evaluation_expression2(self):
        script = dedent("""
        Match(short_description, ?hr_service);
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.type_name, engine.TypeName('Match', None))
        self.assertEqual(cmd.args, engine.ListExpr(
            [engine.ArgumentExpr(engine.BaseExpr('variable', 'short_description'), None),
             engine.ArgumentExpr(None, engine.Projection(None, 'hr_service'))]))

    def test_evaluation_expression3(self):
        script = dedent("""
        Match(short_description, ?hr_service)?matched;
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.type_name, engine.TypeName('Match', None))
        self.assertEqual(cmd.args, engine.ListExpr(
            [engine.ArgumentExpr(engine.BaseExpr('variable', 'short_description'), None),
             engine.ArgumentExpr(None, engine.Projection(None, 'hr_service'))]))
        self.assertEqual(cmd.projection, engine.Projection(None, 'matched'))

    def test_evaluation_expression4(self):
        script = dedent("""
        match(short_description, ?hr_service)?matched;
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.variable_name, 'match')
        self.assertEqual(cmd.args, engine.ListExpr(
            [engine.ArgumentExpr(engine.BaseExpr('variable', 'short_description'), None),
             engine.ArgumentExpr(None, engine.Projection(None, 'hr_service'))]))
        self.assertEqual(cmd.projection, engine.Projection(None, 'matched'))

    def test_evaluation_expression5(self):
        script = dedent("""
        Match(short_description, ['a', 'b', 'c']);
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.type_name, engine.TypeName('Match', None))
        self.assertEqual(cmd.args, engine.ListExpr(
            [engine.ArgumentExpr(engine.BaseExpr('variable', 'short_description'), None),
             engine.ArgumentExpr(engine.ListExpr([engine.BaseExpr('constant', engine.Constant('string', 'a')),
                                                  engine.BaseExpr('constant', engine.Constant('string', 'b')),
                                                  engine.BaseExpr('constant', engine.Constant('string', 'c'))]),
                                 None)]))
        self.assertEqual(cmd.projection, None)

    def test_arithmetic_expression1(self):
        script = dedent("""
        a + c + 3;
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.op, '+')
        self.assertEqual(cmd.expr1, engine.ArithmeticExpr('+', 'a', 'c'))
        self.assertEqual(cmd.expr2, engine.Constant('int', 3))

    def test_arithmetic_expression2(self):
        script = dedent("""
        a + (c + 3);
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.op, '+')
        self.assertEqual(cmd.expr1, 'a')
        self.assertEqual(cmd.expr2, engine.ArithmeticExpr('+', 'c', engine.Constant('int', 3)))

    def test_arithmetic_expression3(self):
        script = dedent("""
        a + (c.prob + 3);
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.op, '+')
        self.assertEqual(cmd.expr1, 'a')
        self.assertEqual(cmd.expr2, engine.ArithmeticExpr('+', 'c.prob', engine.Constant('int', 3)))

    def test_arithmetic_expression4(self):
        script = dedent("""
        a + (-c + 3);
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.op, '+')
        self.assertEqual(cmd.expr1, 'a')
        self.assertEqual(cmd.expr2, engine.ArithmeticExpr('+',
                                                          engine.ArithmeticExpr('-', 'c', None),
                                                          engine.Constant('int', 3)))

    def test_arithmetic_expression5(self):
        script = dedent("""
        a + (-c + [3, 4]);
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.op, '+')
        self.assertEqual(cmd.expr1, 'a')
        self.assertEqual(cmd.expr2, engine.ArithmeticExpr('+',
                                                          engine.ArithmeticExpr('-', 'c', None),
                                                          engine.ListExpr([engine.BaseExpr('constant',
                                                                                           engine.Constant('int', 3)),
                                                                           engine.BaseExpr('constant',
                                                                                           engine.Constant('int', 4))]
                                                                          )))

    def test_arithmetic_expression6(self):
        script = dedent("""
        a + (-c + "sfsf");
        """)
        with self.assertRaises(ValueError):
            engine.compile_norm(script)

    def test_assignment_expression(self):
        script = dedent("""
        a = Company('google')?*;
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        google = engine.BaseExpr('constant', engine.Constant('string', 'google'))
        self.assertEqual(cmd.variable_name, 'a')
        self.assertEqual(cmd.expr, engine.EvaluationExpr(engine.TypeName('Company', None), None,
                                                         engine.ListExpr([engine.ArgumentExpr(google, None)]),
                                                         engine.Projection(1000000, None)))

    def test_condition_expression(self):
        script = dedent("""
        a + c < 10;
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        self.assertEqual(cmd.aexpr, engine.ArithmeticExpr('+', 'a', 'c'))
        self.assertEqual(cmd.op, '<')
        self.assertEqual(cmd.qexpr, engine.BaseExpr('constant', engine.Constant('int', 10)))

    def test_condition_assignment_expression(self):
        script = dedent("""
        a = Company(name ~ 'google')?*;
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        google = engine.BaseExpr('constant', engine.Constant('string', 'google'))
        condition = engine.ConditionExpr('name', '~', google)
        self.assertEqual(cmd.variable_name, 'a')
        self.assertEqual(cmd.expr, engine.EvaluationExpr(engine.TypeName('Company', None), None,
                                                         engine.ListExpr([engine.ArgumentExpr(condition, None)]),
                                                         engine.Projection(1000000, None)))

    def test_property_access_expression(self):
        script = dedent("""
        Company(name ~ 'google').founders;
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        google = engine.BaseExpr('constant', engine.Constant('string', 'google'))
        condition = engine.ConditionExpr('name', '~', google)
        self.assertEqual(cmd.expr, engine.EvaluationExpr(engine.TypeName('Company', None), None,
                                                         engine.ListExpr([engine.ArgumentExpr(condition, None)]),
                                                         None))
        self.assertEqual(cmd.property, 'founders')

    def test_aggregation_function_expression(self):
        script = dedent("""
        Company(name ~ 'google')?*.Group(by="founders");
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        google = engine.BaseExpr('constant', engine.Constant('string', 'google'))
        condition = engine.ConditionExpr('name', '~', google)
        assignment = engine.AssignmentExpr('by', engine.BaseExpr('constant', engine.Constant('string', 'founders')))
        self.assertEqual(cmd.qexpr, engine.EvaluationExpr(engine.TypeName('Company', None), None,
                                                          engine.ListExpr([engine.ArgumentExpr(condition, None)]),
                                                          engine.Projection(1000000, None)))
        self.assertEqual(cmd.eexpr, engine.EvaluationExpr(engine.TypeName('Group', None), None,
                                                          engine.ListExpr([engine.ArgumentExpr(assignment, None)]),
                                                          None))

    def test_combined_condition_expression(self):
        script = dedent("""
        Company((name ~ 'google') & !(name ~ 'microsoft'));
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        google = engine.BaseExpr('constant', engine.Constant('string', 'google'))
        microsoft = engine.BaseExpr('constant', engine.Constant('string', 'microsoft'))
        condition1 = engine.ConditionExpr('name', '~', google)
        condition2 = engine.ConditionExpr('name', '~', microsoft)
        condition = engine.ConditionCombinedExpr('&', condition1, engine.ConditionCombinedExpr('!', condition2, None))
        self.assertEqual(cmd.type_name, engine.TypeName('Company', None))
        self.assertEqual(cmd.args, engine.ListExpr([engine.ArgumentExpr(condition, None)]))

    def test_combined_evaluation_expression(self):
        script = dedent("""
        Company(name ~ 'google')?comp & Develop(comp, 'AI');
        """)
        exe = engine.compile_norm(script)
        cmd = exe.stack.pop()
        google = engine.BaseExpr('constant', engine.Constant('string', 'google'))
        ai = engine.BaseExpr('constant', engine.Constant('string', 'AI'))
        comp = engine.BaseExpr('variable', value='comp')
        condition = engine.ConditionExpr('name', '~', google)
        expr1 = engine.EvaluationExpr(engine.TypeName('Company', None), None,
                                      engine.ListExpr([engine.ArgumentExpr(condition, None)]),
                                      engine.Projection(None, 'comp'))
        expr2 = engine.EvaluationExpr(engine.TypeName('Develop', None), None,
                                      engine.ListExpr([engine.ArgumentExpr(comp, None),
                                                       engine.ArgumentExpr(ai, None)]),
                                      None)

        self.assertEqual(cmd.op, '&')
        self.assertEqual(cmd.expr1, expr1)
        self.assertEqual(cmd.expr2, expr2)
