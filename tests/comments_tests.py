"""Unit tests for Norm"""
from norm.engine import ParseError
from tests.utils import NormTestCase


class CommentsTestCase(NormTestCase):

    def test_recognize_single_line_comment(self):
        self.execute("# comment 1")

    def test_recognize_single_line_comment_description(self):
        res = self.execute("""
        # comment
        test:: String
        """)
        self.assertEqual(res.type_.description, ' comment')

    def test_fail_single_line_comment(self):
        with self.assertRaises(ParseError):
            self.execute("""
            # 
            Comment 3
            """)

    def test_recognize_multi_line_comment(self):
        res = self.execute("""
        '''
          multi-line comment
        '''
        test:: String
        """)
        self.assertEqual(res.type_.description, "\n  multi-line comment\n")

    def test_recognize_multi_line_comments(self):
        res = self.execute("""
        '''
          comment
          and
          more ...
        '''
        test:: String
        """)
        self.assertEqual(res.type_.description, "\n  comment\n  and\n  more ...\n")

    def test_fail_multi_line_comment(self):
        with self.assertRaises(ParseError):
            self.execute("""
                         '''
                             comment
                             no end
                         """)

