import unittest
from title import extract_title

class TestExtractTitle(unittest.TestCase):
    def test_happy_path(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_ignores_other_headings(self):
        md = "## Not a title\n# Real Title\nSome text"
        self.assertEqual(extract_title(md), "Real Title")

    def test_no_title_raises(self):
        with self.assertRaises(ValueError):
            extract_title("## No H1 here\nMore text")
