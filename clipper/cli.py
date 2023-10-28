from . import clipper
from .config import CONFIG, OPTIONS, CONFIG_FILE, Format
from .colors import c, init_colors
from .util import warn
from typing import Optional
import argparse
import importlib
import sys


def get_version():
    """
    Returns the version of the app from version.py
    """
    try:
        version = importlib.import_module("clipper._version")
        return version.version or "0.0.0"
    except ModuleNotFoundError:
        return "0.0.0"


def __init_args(argv: Optional[list] = None) -> str:
    """
    Sets up an argument parser, parses argv, and initializes OPTIONS and CONFIG\n
    Returns the query string passed in.
    """
    parser = argparse.ArgumentParser()

    # Actions
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the current command line options to the configuration.",
    )
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Open the configuration file in your default editor.",
    )
    parser.add_argument(
        "-e",
        "--edit",
        action="store_true",
        help="Open the selected snippet in your configured editor",
    )
    parser.add_argument(
        "-p",
        "--paste",
        action="store_true",
        help="Interactively create a new snippet from clipboard contents (Mac only)",
    )

    # Configuration Options
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="If a file contains multiple snippets, output all of them (no menu)",
    )
    parser.add_argument(
        "--notes",
        action=argparse.BooleanOptionalAction,
        help="Display the full content of the snippet",
    )
    parser.add_argument(
        "-c",
        "--copy",
        action=argparse.BooleanOptionalAction,
        help="Copy the output to the clibpoard (also displays on STDOUT)",
    )
    parser.add_argument(
        "--highlight",
        action=argparse.BooleanOptionalAction,
        help="Use pygments or skylighting to syntax highlight (if installed)",
    )
    parser.add_argument(
        "--blockquotes",
        action=argparse.BooleanOptionalAction,
        help="Include block quotes in output",
    )
    parser.add_argument(
        "-n",
        "--name-only",
        action=argparse.BooleanOptionalAction,
        help="Only search file names, not content",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output format",
        choices=[f.name for f in Format],
        default=CONFIG.output,
    )
    parser.add_argument("-s", "--source", help="Folder to search.")

    # Misc Other Arguments
    # if true, lb=false, interactive=false
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Skip menus and display first match."
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_version(),
        help="Display version information",
    )

    # The search query
    parser.add_argument("query", nargs="*")

    args = parser.parse_args(argv)
    CONFIG.update_from_args(args)
    OPTIONS.parse_args(args)
    return " ".join(args.query)


def main(argv: Optional[list] = None) -> Optional[int]:
    """
    Main entry point for CLI, argv should be sys.argv. Returns None on success,
    1 if there was a failure.
    """
    CONFIG.read_config()
    query = __init_args(argv)
    init_colors()

    if OPTIONS.save_config:
        CONFIG.write_config()
        print(f"{c('bg')}Configuration saved to {c('w')}{CONFIG_FILE}")

    if OPTIONS.edit_config:
        CONFIG.write_config()
        clipper.open_file_in_editor(CONFIG_FILE, CONFIG.editor)
        return

    if not CONFIG.source.is_dir():
        print(f"{c('br')}The Snippets folder doesn't exist, please configure it.")
        print(
            f"{c('bg')}Run `{c('bw')}snibbets --configure{c('bg')}` to open the config file for editing"
        )
        return

    if OPTIONS.paste_snippet:
        clipper.new_snippet_from_clipboard(OPTIONS.edit_snippet)
        return

    if not query:
        if OPTIONS.save_config:
            return
        print(f"{c('br')}No search query.")
        sys.exit(1)

    files = clipper.find_files(query)
    if not files:
        if CONFIG.interactive:
            warn(f"{c('br')}No results")
        return

    snippet_file = clipper.select_file(files)

    if OPTIONS.edit_snippet:
        clipper.open_file_in_editor(snippet_file, CONFIG.editor)
        return

    snippets = clipper.load_snippets(snippet_file)
    if not snippets:
        warn(f"{c('br')}No snippets found.")
        return
    clipper.select_snippet(snippets, snippet_file, query)


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
