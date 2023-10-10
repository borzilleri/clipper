from . import util, snippet, highlighter, menus, languages
from .config import CONFIG, OPTIONS
from .util import warn
from pathlib import Path
from typing import Optional, List
import json
import regex as re
import signal
import sys


def open_file_in_editor(filepath: str, config_editor: Optional[str]):
    editor = config_editor if config_editor is not None else util.best_editor()
    util.open_file(filepath, editor)


def select_snippet(snippets: list, filepath, query):
    selection = menus.menu(
        snippets + [{"title": "All snippets"}], "Select snippet", filepath, query
    )
    if not selection:
        return

    if selection["title"] == "All snippets":
        if CONFIG.output == "json":
            print_snippet(json.dumps(snippets), filepath)
        else:
            if sys.stdout.isatty():
                header = Path(filepath).stem
                warn(f"{header}\n{'='*len(header)}\n")
            print_all(snippets, filepath)
    elif CONFIG.output == "json":
        print_snippet(json.dumps(selection), filepath)
    else:
        if sys.stdout.isatty():
            header = f"{Path(filepath).stem}: {selection['title']}"
            warn(f"{header}\n{'-'*len(header)}\n")
        print_snippet(selection["code"], filepath, selection["lang"])


def handle_results(results: List[dict], query: str):
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

    if OPTIONS.edit_snippet:
        open_file_in_editor(filepath, CONFIG.editor)
        return

    with open(filepath) as f:
        lines = f.read().splitlines()

    snippets = snippet.parse_file(lines, CONFIG.all_notes, CONFIG.include_blockquotes)
    if len(snippets) == 0:
        if CONFIG.interactive:
            warn("No snippets found")
        return
    elif len(snippets) == 1 or not CONFIG.interactive:
        if CONFIG.output == "json":
            print(json.dumps(snippets), filepath)
        else:
            for s in snippets:
                if sys.stdout.isatty():
                    header = Path(filepath).stem
                    print(f"{header}\n{'-'*len(header)}\n")
                print_snippet(s["code"], filepath, s["lang"])
    else:
        if CONFIG.all:
            print_all(snippets, filepath)
        else:
            select_snippet(snippets, filepath, query)


def print_snippet(output: str, filepath: str, lang: str = ""):
    if CONFIG.copy:
        util.copy(output if CONFIG.all_notes else snippet.clean_code(output))
        warn("Copied to clipboard")
    # Only highlight if we're attached to a tty and using raw output,.
    if CONFIG.highlight and CONFIG.output == "raw" and sys.stdout.isatty():
        output = highlighter.highlight(output, filepath, lang, CONFIG.highlight_theme)
    if CONFIG.all_notes:
        print(output)
    else:
        print(snippet.clean_code(output))


def print_all(snippets: list[dict], filepath):
    if CONFIG.output == "json":
        print_snippet(json.dumps(snippets), filepath)
    else:
        is_first = True
        for s in snippets:
            if not is_first:
                print("")
            is_first = False
            print(f"### {s['title']} ###")
            print("")
            print_snippet(s["code"], filepath, s["lang"])


def new_snippet_from_clipboard():
    if not sys.stdout.isatty():
        return

    def signal_handler(s, frame):
        warn("\nCancelled")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    text = snippet.outdent(util.paste())
    title = input("What does this snippet do?").strip()
    langs = input(
        "What language(s) does it use (separate with spaces, full names or file extensions)"
    ).strip()
    langs = [l.strip() for l in re.split(r" +", langs)]

    exts = [e for e in (languages.lang_to_ext(l) for l in langs) if e]
    if len(exts) == 0:
        exts = langs

    tags = sorted(
        [t for t in set([languages.ext_to_lang(l) for l in langs] + langs) if t]
    )

    filename = f"{title}{' '.join([f'.{x}' for x in exts])}{CONFIG.extension}"
    filepath = Path(CONFIG.source, filename)
    with open(filepath, "w") as f:
        print(f"tags: {', '.join(tags)}\n```\n{text}\n```", f)

    print(f"New snippet written to {filename}")
    if OPTIONS.edit_snippet:
        open_file_in_editor(str(filepath), CONFIG.editor)
