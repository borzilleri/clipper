from . import clipper, search
from .config import CONFIG, OPTIONS, CONFIG_FILE, Format
from typing import Optional
import argparse
import importlib
import sys

def get_version():
    try:
        version = importlib.import_module("clipper._version")
        return version.version or "0.0.0"
    except ModuleNotFoundError:
        return "0.0.0"

def get_cli_args(argv: Optional[list] = None) -> argparse.Namespace:
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
    return parser.parse_args(argv)


def main(argv: Optional[list] = None):
    CONFIG.read_config()
    args = get_cli_args(argv)
    CONFIG.update_from_args(args)
    OPTIONS.parse_args(args)

    if OPTIONS.save_config:
        CONFIG.write_config()
        print(f"Configuration saved to {CONFIG_FILE}")

    if OPTIONS.edit_config:
        CONFIG.write_config()
        clipper.open_file_in_editor(str(CONFIG_FILE), CONFIG.editor)
        sys.exit()

    if not CONFIG.source.is_dir():
        print(f"The Snippets folder doesn't exist, please configure it.")
        print(f"Run `snibbets --configure` to open the config file for editing")
        sys.exit()

    if OPTIONS.paste_snippet:
        clipper.new_snippet_from_clipboard()
        sys.exit()

    query = " ".join(args.query)
    if query is None or len(query) == 0:
        if OPTIONS.save_config:
            sys.exit()
        print("No search query.")
        sys.exit(1)

    result = search.search(query, CONFIG.source, CONFIG.extension, CONFIG.name_only)
    if result is not None:
        clipper.handle_results(search.parse_results(result), query)


if __name__ == "__main__":
    main()
