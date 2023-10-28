from .colors import c
from .util import warn
from pathlib import Path
from typing import Optional, List, Dict
import regex as re
import shlex
import shutil
import subprocess


def __do_cmd(cmd: Optional[str]) -> List[str]:
    if cmd:
        out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if out.stdout and len(out.stdout) > 0:
            return out.stdout.strip().split("\n")
    return []


def __grep_cmd(query: str, ext: str, folder: str):
    # Use grep, or grep equivalent
    rg = shutil.which("rg")
    ag = shutil.which("ag")
    ack = shutil.which("ack")
    grep = shutil.which("grep")
    if rg is not None:
        return f"{rg} -li --color=never --glob='*.{ext}' '{query}' {folder}"
    if ag is not None:
        return f"{ag} -li --nocolor -G '.*.{ext}' '{query}' {folder}"
    if ack is not None:
        return f"{ack} -li --nocolor --markdown '{query}' {folder}"
    if grep is not None:
        return f"{grep} -iElr --include '*.{ext}' '{query}' {folder}"
    return None


def __mdfind_cmd(query: str, folder: str, ext: str, name_only: bool) -> Optional[str]:
    mdfind = shutil.which("mdfind")
    if mdfind:
        name_only_opt = "-name " if name_only else ""
        return f"{mdfind} -onlyin {folder} {name_only_opt}'{query} filename:.{ext}'"
    return None


def __find_cmd(query: str, folder: str, ext: str) -> Optional[str]:
    return f"find {folder} -regex '{folder}/{query}' -name '*.{ext}'"


def search(query: str, source_dir: Path, ext: str, name_only: bool) -> list[str]:
    """
    Use multiple methods to search for snippet files and return a list of filepaths.\n
    This will use `mdfind` if available, then `find`, and finally `grep` (and
    several grep-like tools). Grep will only be tried if name_only is false.\n
    Returns None if no results are found.
    """
    query_re = re.sub(r"\s+", ".*", query)
    query_re = f".*{query_re}.*"
    folder = shlex.quote(str(source_dir))

    result = __do_cmd(__mdfind_cmd(query, folder, ext, name_only))
    if result:
        return result

    result = __do_cmd(__find_cmd(query, folder, ext))
    if result:
        return result

    # If we're configured for name_only,
    # don't try grep and just bail here.
    if name_only:
        warn(f"{c('br')}No name matches found.")
        return []

    cmd = __grep_cmd(query, folder, ext)
    # if we didn't find a grep command, print a message and bail.
    if not cmd:
        warn(
            f"{c('br')}No search method available on this system. Please install ripgrep, silver surfer, ack, or grep."
        )
        return []
    return __do_cmd(cmd)


def parse_results(files: List[str]) -> List[Dict[str, str]]:
    """
    Parses a list of file paths into a dictionary of titles and paths.\n
    The title is extracted from the basename of the file.
    """
    # We want unique results, so we convert this to a dict with file path
    # as the key, ensuring only one entry per file path
    results = {f: {"title": Path(f).stem, "path": f} for f in files}.values()
    sorted(results, key=lambda l: l["title"])
    return list(results)
