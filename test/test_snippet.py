from clipper import snippet
import unittest
from unittest.mock import patch

snippet_fenced_code = """title: A snippet with a code block
### This is a code block

```java
This is java code
```
"""
snippet_indent_code = """title: A snippet with a code block
### This is a code block

    Indent Line 1
"""
snippet_replaced_block = f"""title: A snippet with a code block
### This is a code block

<block:1>"""
snippet_blockquote_fence = """title: A snippet with a block quote
### This snippet has blockquotes

> blockquote comment

```java
This is java code
```
"""
snippet_blockquote_replaced_indent = f"""title: A snippet with a block quote
### This snippet has blockquotes

<block:1>
<block:2>"""

indented_code = """
    line 1
    
    line 2
    

"""
expected_outdent = """line 1

line 2"""


class TestSnippet(unittest.TestCase):
    @patch("uuid.uuid4")
    def test_replace_blocks_fenced(self, mock_uuid):
        mock_uuid.side_effect = [1]
        (out, code) = snippet.extract_code(snippet_fenced_code, False)
        self.assertEqual(out, snippet_replaced_block)
        self.assertDictEqual(code, {f"block:1": "<lang:java>\nThis is java code"})

    @patch("uuid.uuid4")
    def test_replace_blocks_indented(self, mock_uuid):
        mock_uuid.side_effect = [1]
        (out, code) = snippet.extract_code(snippet_indent_code, False)
        self.assertEqual(out, snippet_replaced_block)
        self.assertDictEqual(code, {f"block:1": "Indent Line 1"})

    @patch("uuid.uuid4")
    def test_replace_blocks_with_blockquotes(self, mock_uuid):
        mock_uuid.side_effect = [1,2]
        (out, code) = snippet.extract_code(snippet_blockquote_fence, True)
        self.assertEqual(out, snippet_blockquote_replaced_indent)
        self.assertDictEqual(
            code,
            {
                f"block:1": "# blockquote comment",
                f"block:2": "<lang:java>\nThis is java code",
            },
        )

    def test_parse_lang_marker(self):
        block_without_lang = "Code Block"
        block_with_lang = f"<lang:java>\n{block_without_lang}"
        lang, code = snippet.parse_lang_marker(block_without_lang)
        self.assertEqual(lang, '')
        self.assertEqual(code, block_without_lang)
        lang, code = snippet.parse_lang_marker(block_with_lang)
        self.assertEqual(lang, "java")
        self.assertEqual(code, block_without_lang)

    def test_outdent(self):
        actual = snippet.outdent(indented_code)
        self.assertEqual(actual, expected_outdent)

    def test_remove_metadata_no_meta(self):
        lines = ["foo", "a:b", "bar"]
        out = snippet.remove_metadata(lines)
        self.assertEqual(out, ["foo","a:b","bar"])

    def test_remove_metadata_with_meta(self):
        lines = ["title: b", "foo", "a:b", "bar"]
        out = snippet.remove_metadata(lines)
        self.assertEqual(out, ["foo","a:b","bar"])

    def test_remove_metadata_with_spacer(self):
        lines = ["----", "foo", "a:b", "bar"]
        out = snippet.remove_metadata(lines)
        self.assertEqual(out, ["foo","a:b","bar"])

    def test_remove_metadata_with_meta_and_spacer(self):
        lines = ["title:b", "----", "foo", "a:b", "bar"]
        out = snippet.remove_metadata(lines)
        self.assertEqual(out, ["foo","a:b","bar"])
