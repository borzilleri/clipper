from .util import trim_list, strip_empty_lines, is_fenced
from typing import Tuple, List, Dict
import regex as re
import uuid

BLOCK_RE = re.compile(
    r"<(block:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})>"
)
HEADER_RE = re.compile(r"(^#+|#+$)")


def __make_block_id():
    return f"block:{str(uuid.uuid4())}"


def extract_code(text: str, blockquotes: bool) -> Tuple[str, dict]:
    """
    Extract code blocks from the snippet, and return them in a separate array
    """
    code_blocks = {}

    # If we should include blockquote comments,
    # also extract them as code blocks.
    if blockquotes:
        # Find lines that start with a '>' followed by anything,
        # up to either a newline, or the end of the line.
        matches = re.finditer(r"(^(>.*?)(\n|$))+", text, flags=re.M | re.I)
        for m in matches:
            block_id = __make_block_id()
            # Replace the '>' with '#', and shove it into our code blocks dict
            code_blocks[block_id] = re.sub(r"^> *(?=\S)", "# ", m.group(0).strip())
            text = text.replace(m.group(0), f"<{block_id}>")

    # find and extract backtick-enclosed code blocks
    matches = re.finditer(
        r"^(`{3,})( *\S+)? *\n([\s\S]*?)\n(`{3,}) *(\n|\Z)", text, flags=re.M | re.I
    )
    for m in matches:
        lang = f"<lang:{m.group(2).strip()}>\n" if m.group(2) else ""
        block_id = __make_block_id()
        code_blocks[block_id] = f"{lang}{m.group(3)}".strip()
        text = text.replace(m.group(0), f"<{block_id}>")

    # find and extract indented code blocks
    matches = re.finditer(
        r"(?<=\n\n|\A)\n?((?: {4,}|\t+)\S[\S\s]*?)(?=\n\S|\Z)",
        text,
        flags=re.M | re.I,
    )
    for m in matches:
        block_id = __make_block_id()
        code_blocks[block_id] = outdent(m.group(1)).strip()
        text = text.replace(m.group(0), f"<{block_id}>")
    return (text, code_blocks)


# Does this part have any non-code notes in it?
def has_notes(text: str):
    notes = list(
        filter(
            lambda el: not re.search(f"^{BLOCK_RE.pattern}$", el)
            and not re.search(r"^```", el)
            and len(el.strip()) > 0,
            text.split("\n"),
        )
    )
    return len(notes) > 0


def restore_code(part: str, blocks: Dict[str, str]) -> Dict[str, str]:
    # if this part has any blocks in it
    # OR has any notes in it (because all_notes=True),
    # Then, build a dict with the title, lang, and text
    snippet = {"title": "Default snippet", "lang": "", "code": ""}
    # Does this part have any code block tags in it?
    block_tags = BLOCK_RE.findall(part)

    if block_tags or has_notes(part):
        # Extract the title from the first line
        # Grab the first line, check to see if it's a block tag
        title_m = re.search(r"\A(.+)\n", part)
        if title_m and not BLOCK_RE.search(title_m.group(0)):
            # if not, extract it as the title.
            snippet["title"] = re.sub(r"[.:]$", "", title_m.group(0).strip())
            part = part.replace(title_m.group(0), "")
        for tag in block_tags:
            this_lang, this_code = parse_lang_marker(strip_empty_lines(blocks[tag]))
            # Set our overall snippet language to the first one we find.
            if not snippet["lang"] and this_lang:
                snippet["lang"] = this_lang
            part = part.replace(f"<{tag}>", f"```{this_lang}\n{this_code}\n```")
        snippet["code"] = part
    return snippet


def parse_lang_marker(block: str):
    lang = ""
    code = block
    m = re.search(r"<lang:(.*?)>", block)
    if m:
        lang = m.group(1)
        code = strip_empty_lines(re.sub(r"<lang:.*?>\n+", "", block))
    return (lang, code)


def outdent(val: str) -> str:
    lines = val.split("\n")
    incode = False
    code = []
    for line in lines:
        if not re.search(r"^\s*$", line) or incode:
            incode = True
            code.append(line)
    if len(code) == 0:
        return val
    indent = re.search(r"^( {4,}|\t+)(?=\S)", code[0])
    if indent is None:
        return val
    code = [re.sub(rf"^{indent[1]}", "", l, flags=re.M | re.I) for l in code]
    return "\n".join(code).strip()


def clean_code(block: str):
    """
    Cleans non-code bits from fenced code blocks or indented code blocks.\n
    Fences are discarded, indented code is un-indented, and anything outside is
    discarded.
    """
    # if we're a fenced code block, discard the fences
    # and anything outside
    if is_fenced(block):
        code_blocks = re.findall(r"(`{3,})(\S+)?\s*\n(.*?)\n\1", block, re.M)
        code_blocks = [x[2].strip() for x in code_blocks]
        return "\n\n".join(code_blocks)
    # Otherwise, assume its intended.
    # discard non-intended lines and return the rest
    if re.search(r"^( {4,}|\t+)", block):
        block = outdent(block)
    return block


def remove_metadata(lines: List[str]) -> List[str]:
    """
    Remove any MultiMarkdown style metadata & separator lines from the start of
    the list
    """
    idx = 0
    for line in lines:
        meta_match = re.search(r"^\s*[a-z\s]+\w:\s*\S+", line, flags=re.I)
        spacer_match = re.search(r"^-{3,}\s*$", line)
        if not meta_match and not spacer_match:
            break
        else:
            idx += 1
    return lines[idx:]


def strip_notes(part: str) -> str:
    # Split the part into lines, and extract the first as the title.
    lines = part.split("\n")
    title = HEADER_RE.sub("", lines[0]) if len(lines) > 0 else None
    lines = lines[1:]
    # if this part has a block
    if BLOCK_RE.search(part):
        # strip out any lines that aren't a code block or a blockquote.
        lines = list(filter(lambda l: l.startswith("#") or BLOCK_RE.search(l), lines))
        lines = [HEADER_RE.sub("", l) for l in lines]
    new_part = "\n".join(lines)
    if title:
        new_part = f"{title}\n{new_part}"
    return new_part


def parse_file(
    lines: List[str], all_notes: bool, blockquotes: bool
) -> List[Dict[str, str]]:
    # Strip out metadata, and combine the lines into a single string
    file = "\n".join(trim_list(remove_metadata(lines)))
    # extract code blocks (&maybe blockquotes)
    (text, blocks) = extract_code(file, blockquotes)
    # replace any groups of 2+ newlines with just two newlines
    text = re.sub(r"\n{2,}", "\n\n", text)
    # split the text into individual snippets at the ATX-style headers
    parts = trim_list(re.split(r"^#+\s*", text, flags=re.M))
    if not all_notes:
        parts = (strip_notes(p) for p in parts)
    # finally, replace the code blocks
    snippets = (restore_code(part, blocks) for part in parts)
    # Remove any that don't have code
    snippets = (s for s in snippets if s["code"])
    return list(snippets)
