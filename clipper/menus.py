from .config import CONFIG
from .util import warn
from typing import Optional, Dict
from pick import pick
import regex as re
import shlex
import shutil

MENUS = ["fzf", "gum"]


def find_query_in_options(data: list, filename: str, query: str) -> list:
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


def remove_items_without_query(data: list, filename: str, query: str):
    q = find_query_in_options(data, filename, query)

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


def best_menu(selection: Optional[str]):
    # If the selection exists, use it
    if selection and (selection == "console" or shutil.which(selection)):
        return selection
    # Otherwise, look for the first available option
    for m in MENUS:
        if shutil.which(m):
            return m
    # or default to console.
    return "console"


def menu_gum(
    input: list, title: str, filename: Optional[str] = None, query: Optional[str] = None
):
    raise NotImplementedError


def menu_fzf(
    input: list, title: str, filename: Optional[str] = None, query: Optional[str] = None
):
    raise NotImplementedError


def menu_pick(
    data: list, title: str, filename: Optional[str] = None, query: Optional[str] = None
) -> Optional[Dict[str, str]]:
    if query and len(query) > 0:
        data = remove_items_without_query(data, filename or "", query)
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
    menu = best_menu(CONFIG.menus)
    if query:
        words = list(filter(lambda w: re.search(r"^\w:", w), shlex.split(query)))
        query = " ".join(words).strip()

    if menu == "gum":
        menu_gum(data, title, filename, query)
    elif menu == "fzf":
        menu_fzf(data, title, filename, query)
    else:
        return menu_pick(data, title, filename, query)
