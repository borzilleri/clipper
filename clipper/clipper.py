from . import util, snippet, menus, languages, printer
from .config import CONFIG, OPTIONS
from .colors import c
from .util import warn
from pathlib import Path
from typing import Optional, List
import regex as re
import signal
import sys


def open_file_in_editor(filepath: str, config_editor: Optional[str]):
    editor = config_editor if config_editor is not None else util.best_editor()
    util.open_file(filepath, editor)


def select_snippet(snippets: list, filepath, query) -> list[dict[str,str]]:
    selection = menus.menu(
        snippets + [{"title": "All snippets"}], "Select snippet", filepath, query
    )
    if not selection:
        return []
    if selection["title"] == "All snippets":
        return snippets
    else:
        return [selection]


def handle_results(results: List[dict], query: str):
    # Select our file from the search results.
    if len(results) == 0:
        if CONFIG.interactive:
            warn("No results")
        return
    elif len(results) == 1 or not CONFIG.interactive:
        filepath = results[0]["path"]
    else:
        answer = menus.menu(results, "Select a file")
        if not answer:
            return
        filepath = answer["path"]

    # Open up the editor if necessary,
    # that's all we'll do this time.
    if OPTIONS.edit_snippet:
        open_file_in_editor(filepath, CONFIG.editor)
        return

    # Now that we have our snippet file,
    # read the contents and parse the snippets.
    with open(filepath) as f:
        lines = f.read().splitlines()
    snippets = snippet.parse_file(lines, CONFIG.all_notes, CONFIG.include_blockquotes)
    
    if len(snippets) > 1 and not CONFIG.all and CONFIG.interactive:
            snippets = select_snippet(snippets, filepath, query)
    
    if len(snippets) == 0:
        if CONFIG.interactive:
            warn("No snippets found")
        return
    printer.print_snippets(snippets, filepath)

def new_snippet_from_clipboard():
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
    if OPTIONS.edit_snippet:
        open_file_in_editor(str(filepath), CONFIG.editor)
