from . import highlighter, util, snippet
from .config import CONFIG, Format
from .colors import c
from pathlib import Path
import json
import sys


def __print_json(clips: list[dict[str, str]]):
    """
    Print the list of clips as JSON output.\n
    Notes will be trimmed if the all_notes is false.\n
    The entire json output will be copied if copy=true.\n
    No highlighting is done on JSON output.\n
    """
    if not CONFIG.all_notes:
        for c in clips:
            c.update({"code": snippet.clean_code(c["code"])})
    output = json.dumps(clips)
    if CONFIG.copy:
        util.copy(output)
        util.warn("Copied to clipboard")
    print(output)


def __print_single(clip: dict[str, str], filepath: str):
    """
    Prints a single snippet to stdout.\n
    A header with the filename and title will be printed to stderr.\n
    If set to copy, code block (with notes if applicable) will be copied.
    """
    if CONFIG.copy:
        util.copy(
            clip["code"] if CONFIG.all_notes else snippet.clean_code(clip["code"])
        )
        util.warn("Copied to clipboard")
    header = f"{c('bw')}{Path(filepath).stem}: {c('c')}{clip['title']}{c('x')}"
    util.warn(f"{header}\n{c('dw')}{'-'*len(header)}{c('x')}\n")
    output = clip["code"]
    if CONFIG.highlight and sys.stdout.isatty():
        # Only highlight if we're attached to a tty
        output = highlighter.highlight(
            output, filepath, clip["language"], CONFIG.highlight_theme
        )
    if CONFIG.all_notes:
        print(output)
    else:
        print(snippet.clean_code(output))


def __print_multiple(clips: list[dict[str, str]], filepath: str):
    """
    Prints multiple snippets to stdout.\n
    A header with the filename will be printed to stderr.\n
    If set to copy, the entire output (except the header) will be copied.
    """
    copy_out = ""
    std_out = ""
    prefix = ""
    for clip in clips:
        title = (
            f"{prefix}{c('dw')}### {c('xbw')}{clip['title']} {c('xdw')}###{c('x')}\n\n"
        )
        std_out += title
        copy_out += title
        this_code = clip["code"]
        if not CONFIG.all_notes:
            this_code = snippet.clean_code(this_code) + "\n"
        copy_out += this_code
        if CONFIG.highlight and sys.stdout.isatty():
            # Only highlight if we're attached to a tty
            this_code = highlighter.highlight(
                this_code, filepath, clip["language"], CONFIG.highlight_theme
            )
        std_out += this_code
        prefix = "\n"
    if CONFIG.copy:
        util.copy(copy_out)
        util.warn("Copied to clipboard")
    header = Path(filepath).stem
    util.warn(f"{c('bw')}{header}\n{c('xdw')}{'-'*len(header)}{c('x')}\n")
    print(std_out)


def print_snippets(clips: list[dict[str, str]], filepath: str):
    """
    Prints a list of snippets in various ways depending on configuration.\n
    Prints in alfred or json output formats, if specified.\n
    Prints a single note if length==1\n
    Prints multiple notes if length>1
    """
    if CONFIG.format == Format.json:
        __print_json(clips)
    elif len(clips) == 1:
        __print_single(clips[0], filepath)
    else:
        __print_multiple(clips, filepath)
