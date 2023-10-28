from . import clipper, snippet
from .config import CONFIG
from pathlib import Path
import hashlib
import json
import sys


def __make_uid(text: str) -> str:
    """
    Hash a string into a UID for alfred.
    """
    return hashlib.sha256(text.encode()).hexdigest()


def transform_clip(
    filepath: str, title: str, language: str, code: str
) -> dict[str, str]:
    """
    Transform snippet data into an output format for alfred results.
    """
    return {
        "uid": __make_uid(title),
        "title": title,
        "subtitle": language,
        "arg": code if CONFIG.all_notes else snippet.clean_code(code),
        "autocomplete": title,
        "quicklookurl": filepath,
    }


def main(argv: list[str]):
    """
    Main entry point for Alfred, argv should be the query the user types,
    usually sys.argv, without the first element (program name).
    """
    CONFIG.read_config()
    # Force all snippets to true for alfred.
    CONFIG.all = True
    items = []

    query = " ".join(argv)
    if query:
        files = clipper.find_files(query)
        for item in files:
            snippets = clipper.load_snippets(Path(item["path"]))
            items.extend([transform_clip(item["path"], **s) for s in snippets])
    print(json.dumps({"items": items}))


if __name__ == "__main__":
    main(sys.argv[1:])
