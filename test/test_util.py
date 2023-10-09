from clipper import util
import unittest


class TestUtil(unittest.TestCase):
    def test_is_bundle(self):
        self.assertTrue(
            util.is_bundle("com.apple.finder"), "is_bundle should be true for bundle id"
        )
        self.assertFalse(
            util.is_bundle("vim"), "is_bundle should be false for cli command."
        )
        self.assertFalse(
            util.is_bundle("Safari"), "is_bundle should be false for app name."
        )

    def test_trim_list(self):
        self.assertEqual(util.trim_list([]), [])
        self.assertEqual(util.trim_list([""]), [])
        self.assertEqual(util.trim_list(["", "a"]), ["a"])
        self.assertEqual(util.trim_list(["a", ""]), ["a"])
        self.assertEqual(util.trim_list(["", "a", ""]), ["a"])
        self.assertEqual(util.trim_list(["", "a", "", "b", ""]), ["a", "", "b"])
        self.assertEqual(util.trim_list(["a"]), ["a"])
        self.assertEqual(util.trim_list(["  "]), [])

    def test_strip_empty_lines(self):
        self.assertEqual(util.strip_empty_lines("abc"), "abc")
        self.assertEqual(util.strip_empty_lines("   \nabc"), "abc")
        self.assertEqual(util.strip_empty_lines(" \nabc\n "), "abc")
        self.assertEqual(util.strip_empty_lines("abc\n \ndef"), "abc\n \ndef")
        self.assertEqual(util.strip_empty_lines(" \nabc\n \ndef\n "), "abc\n \ndef")

if __name__ == "__main__":
    unittest.main()