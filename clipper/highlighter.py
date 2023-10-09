from .config import CONFIG
from typing import Optional

DEFAULT_THEME = "default"


def highlight(text: str, filename: str, lang: str, theme: Optional[str] = None) -> str:
    # if not a TTY
    "return all_notes AND has_notes ? code : clean_code"

    # if we're fenced
    "return highlight_fences(code, filename, lang)"

    theme = theme or CONFIG.highlight_theme or DEFAULT_THEME
    syntax = lang or "Lexers.syntax_from_extension(filename)"
    syntax = "Lexers.normalize_lexer(syntax)"

    if syntax == "text":
        return text
    # haha all of this is dumb we're just using pygments beause its got a
    # python library and fuck anything else.
    return text
