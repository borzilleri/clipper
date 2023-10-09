from .langauge_data import LANGUAGES
from typing import Optional


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
