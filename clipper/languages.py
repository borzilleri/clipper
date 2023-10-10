from .language_data import LANGUAGES
from typing import Optional

SYNTAX_NORMALIZATION = {
  'objectivec': ["objective-c", "obj-c"],
  'markdown': ["md", "mmd", "mkdn", "multimarkdown"],
  'bash': ["csh", "sh", "shell"],
  'javascript': ["js"],
  'javascriptreact': ["react"],
  'yaml': ["yml"]
}

def normalize_syntax(lang: str) -> str:
    for k, v in SYNTAX_NORMALIZATION.items():
        if lang in v:
            return k
    return lang

def lang_to_ext(lang: str) -> Optional[str]:
    """
    Returns the most appropriate file extension from a language.
    """
    lang = lang.lower()
    items = [l for l in LANGUAGES if l["lang"].lower() == lang or lang in l["aliases"]]
    if items:
        return items[0]["exts"][0]
    return lang


def ext_to_lang(ext: str) -> Optional[str]:
    """
    Returns the most appropriate language from a file extension.
    """
    items = [l for l in LANGUAGES if ext.lower() in map(str.lower, l["exts"])]
    if items:
        return items[0]["lang"]
    return ext
