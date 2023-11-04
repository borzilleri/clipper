from .config import CONFIG
from .util import warn
from pathlib import Path
from pick import pick
from typing import Optional, Dict
import regex as re
import shlex
import shutil
import subprocess

__DEFAULT_MENU = "console"
__MENUS = ["fzf", "gum"]


def __find_query_in_options(data: list, filename: str, query: str) -> list:
    options = [f"{filename} {x['title']}" for x in data]
    words = re.split(r" +", query)
    words = list(
        filter(
            lambda w: len(
                list(filter(lambda o: re.search(f"{w}", o, flags=re.I), options))
            )
            > 0,
            words,
        )
    )
    return [w.lower() for w in words]


def __remove_items_without_query(data: list, filename: str, query: str):
    q = __find_query_in_options(data, filename, query)

    result = list(
        filter(
            lambda o: len(
                list(
                    filter(
                        lambda w: re.search(f"{filename} {o['title']}", w, flags=re.I),
                        q,
                    )
                )
            )
            > 0,
            data,
        )
    )
    return result


def __menu_exists(menu: str) -> Optional[str]:
    if menu == __DEFAULT_MENU:
        return menu
    return shutil.which(menu)


def __best_menu(selection: Optional[str]) -> tuple[str, str]:
    # If the selection exists, prefer it, if it exists.
    if selection:
        menu_exe = __menu_exists(selection)
        if menu_exe:
            return (selection, menu_exe)
    # Otherwise, look for the first available option
    for m in __MENUS:
        menu_exe = __menu_exists(m)
        if menu_exe:
            return (m, menu_exe)
    # If all else fails, use our defaults.
    return (__DEFAULT_MENU, __DEFAULT_MENU)


def __menu_gum(
    exe: str, data: list, title: str, filename: str, query: str
) -> Optional[Dict[str, str]]:
    if query and len(query) > 0:
        data = __remove_items_without_query(data, filename or "", query)
        if len(data) == 1:
            return data[0]

    if len(data) == 0:
        if CONFIG.interactive:
            warn("No matches found")
        return None

    choices = [x["title"] for x in data]
    print(title)
    gum_proc = subprocess.Popen(
        [exe, "filter", f"--height={len(choices)}"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    out, _ = gum_proc.communicate(input=("\n".join(choices)).encode())
    selection = out.decode().strip()
    for item in data:
        if selection == item["title"]:
            return item
    return None


def __menu_fzf(
    exe: str, data: list, title: str, filename: str, query: str
) -> Optional[Dict[str, str]]:
    if query and len(query) > 0:
        data = __remove_items_without_query(data, filename or "", query)
        if len(data) == 1:
            return data[0]

    if len(data) == 0:
        if CONFIG.interactive:
            warn("No matches found")
        return None

    filename = Path(filename).stem
    choices = [f"{filename}: {x['title']}" for x in data]
    q = " ".join(__find_query_in_options(data, filename, query)) if query else ""
    fzf_proc = subprocess.Popen(
        [
            exe,
            f"--height={len(choices)+2}",
            f"--prompt={title} > ",
            "-1",
            f"--header={filename}",
            "--reverse",
            "--no-info",
            f"--query={q}",
            "--tac",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    out, _ = fzf_proc.communicate(input=("\n".join(choices)).encode())
    selection = re.sub(r"^.*?: ", "", out.decode().strip())
    for item in data:
        if selection == item["title"]:
            return item
    return None


def __menu_pick(
    data: list, title: str, filename: str, query: str
) -> Optional[Dict[str, str]]:
    if query and len(query) > 0:
        data = __remove_items_without_query(data, filename or "", query)
        if len(data) == 1:
            return data[0]

    if len(data) == 0:
        if CONFIG.interactive:
            warn("No matches found")
        return None

    choices = [x["title"] for x in data]
    _, idx = pick(choices, title)
    return data[int(idx)]  # type: ignore


def menu(
    data: list, title: str, filename: Optional[str] = None, query: Optional[str] = None
) -> Optional[Dict[str, str]]:
    if query:
        words = list(filter(lambda w: re.search(r"^\w:", w), shlex.split(query)))
        query = " ".join(words).strip()

    filename = filename or ""
    query = query or ""

    menu, menu_exe = __best_menu(CONFIG.menus)
    if menu == "gum":
        return __menu_gum(menu_exe, data, title, filename, query)
    elif menu == "fzf":
        return __menu_fzf(menu_exe, data, title, filename, query)
    else:
        return __menu_pick(data, title, filename, query)
