"""Unit tests for Norm"""
from tests.norm.utils import NormTestCase


class CommentsTestCase(NormTestCase):

    def test_recognize_single_line_comment1(self):
        script = """
        // Comment 1
        ;
        """
        res = self.execute(script)
        self.assertEqual(res, 'Comment 1\n')

    def test_recognize_single_line_comment2(self):
        script = """
        // \tComment 2
        ;
        """
        res = self.execute(script)
        self.assertEqual(res, 'Comment 2\n')

    def test_fail_single_line_comment1(self):
        script = """
        // 
        Comment 3
        ;
        """
        with self.assertRaises(ValueError):
            self.execute(script)

    def test_recognize_multi_line_comment1(self):
        script = """
        /* Comment 4 */
        ;
        """
        res = self.execute(script)
        self.assertEqual(res, 'Comment 4')

    def test_recognize_multi_line_comment2(self):
        script = """
        /*
            Comment 5 
        */
        ;
        """
        res = self.execute(script)
        self.assertEqual(res, "Comment 5")

    def test_recognize_multi_line_comment3(self):
        script = """
        /*
            Comment 6
            and
            more ...
        */
        ;
        """
        res = self.execute(script)
        self.assertEqual(res, "Comment 6\n    and\n    more ...")

    def test_fail_multi_line_comment4(self):
        script = """
        /*
            Comment 7
            no end
        """
        with self.assertRaises(ValueError):
            self.execute(script)

