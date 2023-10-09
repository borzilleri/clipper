from clipper import snippet
import unittest

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
snippet_replaced_block = """title: A snippet with a code block
### This is a code block

<block1>
"""
snippet_blockquote_fence = """title: A snippet with a block quote
### This snippet has blockquotes

> blockquote comment

```java
This is java code
```
"""
snippet_blockquote_replaced_indent = """title: A snippet with a block quote
### This snippet has blockquotes

<block1>
<block2>

"""

indented_code = """
    line 1
    
    line 2
    

"""
outdented_code = """line 1

line 2


"""


class TestSnippet(unittest.TestCase):
    def test_replace_blocks_fenced(self):
        (out, code) = snippet.replace_blocks(snippet_fenced_code, False)
        self.assertEqual(out, snippet_replaced_block)
        self.assertDictEqual(code, {"block1": "<lang:java>\nThis is java code"})

    def test_replace_blocks_indented(self):
        (out, code) = snippet.replace_blocks(snippet_indent_code, False)
        self.assertEqual(out, snippet_replaced_block)
        self.assertDictEqual(code, {"block1": "Indent Line 1\n"})

    def test_replace_blocks_with_blockquotes(self):
        (out, code) = snippet.replace_blocks(snippet_blockquote_fence, True)
        self.assertEqual(out, snippet_blockquote_replaced_indent)
        self.assertDictEqual(
            code,
            {
                "block1": "# blockquote comment\n",
                "block2": "<lang:java>\nThis is java code",
            },
        )

    def test_block_count(self):
        out = snippet.block_count(snippet_blockquote_fence.split("\n"))
        self.assertEqual(out, 0)
        out = snippet.block_count(snippet_blockquote_replaced_indent.split("\n"))
        self.assertEqual(out, 2)
        out = snippet.block_count("".split("\n"))
        self.assertEqual(out, 0)

    def test_parse_lang_marker(self):
        block_without_lang = "Code Block"
        block_with_lang = f"<lang:java>\n{block_without_lang}"
        lang, code = snippet.parse_lang_marker(block_without_lang)
        self.assertIsNone(lang)
        self.assertEqual(code, block_without_lang)
        lang, code = snippet.parse_lang_marker(block_with_lang)
        self.assertEqual(lang, "java")
        self.assertEqual(code, block_without_lang)

    def test_outdent(self):
        out = snippet.outdent(indented_code)
        self.assertEqual(out, outdented_code)

    def test_remove_metadata_no_meta(self):
        lines = ["foo", "a:b", "bar"]
        out = snippet.remove_metadata(lines)
        self.assertEqual(out, "foo\na:b\nbar")

    def test_remove_metadata_with_meta(self):
        lines = ["title: b", "foo", "a:b", "bar"]
        out = snippet.remove_metadata(lines)
        self.assertEqual(out, "foo\na:b\nbar")

    def test_remove_metadata_with_spacer(self):
        lines = ["----", "foo", "a:b", "bar"]
        out = snippet.remove_metadata(lines)
        self.assertEqual(out, "foo\na:b\nbar")

    def test_remove_metadata_with_meta_and_spacer(self):
        lines = ["title:b", "----", "foo", "a:b", "bar"]
        out = snippet.remove_metadata(lines)
        self.assertEqual(out, "foo\na:b\nbar")
