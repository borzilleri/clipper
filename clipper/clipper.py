from . import util, snippet, menus, languages, printer, search
from .config import CONFIG, Format
from .colors import c
from .util import warn
from pathlib import Path
from typing import Optional, List
import regex as re
import signal
import sys


def open_file_in_editor(filepath: Optional[Path], config_editor: Optional[str]):
    """Opens the provided file path in the provided editor (or the best availale
    editor if not supplied)"""
    if not filepath:
        return
    editor = config_editor if config_editor is not None else util.best_editor()
    util.open_file(str(filepath), editor)


def select_snippet(snippets: list, filepath, query):
    if len(snippets) > 1 and not CONFIG.all and CONFIG.interactive:
        selection = menus.menu(
            snippets + [{"title": "All snippets"}], "Select snippet", filepath, query
        )
        if not selection:
            return
        if selection["title"] != "All snippets":
            snippets = [selection]
    printer.print_snippets(snippets, filepath)


def select_file(results: List[dict[str, str]]) -> Optional[Path]:
    """
    Selects a single file from a list.\n
    If there's only one file, or we're not interactive, just grab the first
    file.\n
    Otherwise, prompt the user to select a file.
    """
    if len(results) == 1 or not CONFIG.interactive:
        return Path(results[0]["path"])
    else:
        answer = menus.menu(results, "Select a file")
        if answer:
            return Path(answer["path"])


def new_snippet_from_clipboard(with_edit: bool):
    """
    Create a new snippet file from the contents of the clipboard,
    prompting the user for the snippets purpose/filename,
    and language/tags.\n
    If `with_edit` is true, the file will also be opened in an editor.
    """
    if not sys.stdout.isatty():
        return

    def signal_handler(s, frame):
        warn("\nCancelled")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    text = snippet.outdent(util.paste()).strip()
    title = input(f"{c('by')}What does this snippet do?\n> ").strip()
    langs = input(
        f"{c('by')}What language(s) does it use (separate with spaces, full names or file extensions)?\n> "
    ).strip()
    langs = [l.strip() for l in re.split(r" +", langs)]

    exts = [e for e in (languages.lang_to_ext(l) for l in langs) if e]
    if len(exts) == 0:
        exts = langs

    tags = sorted(
        [t for t in set([languages.ext_to_lang(l) for l in langs] + langs) if t]
    )

    filename = f"{title}.{'.'.join([x for x in exts])}.{CONFIG.extension}"
    filepath = Path(CONFIG.source, filename)
    with open(filepath, "w") as f:
        print(f"tags: {', '.join(tags)}\n---\n```\n{text}\n```", file=f)

    print(f"{c('bg')}New snippet written to {c('bw')}{filename}")
    if with_edit:
        open_file_in_editor(filepath, CONFIG.editor)


def find_files(query: str) -> list[dict[str, str]]:
    """
    Search for a snippet file using the given query, allowing the user to select
    one if we're in an interactive session and multiple are returned.
    """
    search_result = search.search(
        query, CONFIG.source, CONFIG.extension, CONFIG.name_only
    )
    return search.parse_results(search_result)


def load_snippets(filepath: Optional[Path]) -> list[dict[str, str]]:
    """
    Read a snippet file and load snippets within it, returning the list.
    """
    if not filepath:
        return []
    with filepath.open() as f:
        lines = f.read().splitlines()
    return snippet.parse_file(lines, CONFIG.all_notes, CONFIG.include_blockquotes)
