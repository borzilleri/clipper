from . import languages
from .util import is_fenced, get_fences
from typing import Optional
from pathlib import Path
import pygments, pygments.lexers, pygments.formatters, pygments.styles

DEFAULT_THEME = "default"


def syntax_from_extension(filename) -> Optional[str]:
    exts = [ext.strip('.') for ext in Path(filename).suffixes[:-1]]
    return languages.ext_to_lang(exts[-1]) if exts else None


def highlight_fences(text: str, filename: str, lang: str, theme: Optional[str] = None):
    fences = get_fences(text)
    for f in fences:
        # escape regex f[code]?
        syntax = languages.normalize_syntax(f["lang"] or lang)
        highlighted_text = highlight(f["code"], filename, syntax).strip()
        text.replace(f["code"], highlighted_text)
    return text

def highlight_pygments(text: str, syntax, theme: str) -> str:
    if syntax:
        lexer = pygments.lexers.get_lexer_by_name(syntax)
    else:
        lexer = pygments.lexers.guess_lexer(text)
    style = pygments.styles.get_style_by_name(theme)
    formatter = pygments.formatters.get_formatter_by_name('terminal16m', style=style)    
    return pygments.highlight(text, lexer=lexer, formatter=formatter)


def highlight(text: str, filename: str, lang: str, theme: Optional[str] = None) -> str:
    theme = theme or DEFAULT_THEME

    if is_fenced(text):
        # We have code fences (enclosed by ```),
        # so highlight the code inside them
        return highlight_fences(text, filename, lang, theme)

    syntax = lang or syntax_from_extension(filename)
    if syntax:
        syntax = languages.normalize_syntax(syntax)

    if syntax == "text":
        return text    

    return highlight_pygments(text, syntax, theme)
