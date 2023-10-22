from .config import CONFIG
from .util import warn
from typing import Optional, Dict
from pick import pick
import regex as re
import shlex
import shutil

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


def __menu_exists(menu: str) -> bool:
    return bool(menu == __DEFAULT_MENU or shutil.which(menu))


def __best_menu(selection: Optional[str]):
    # If the selection exists, use it
    if selection and __menu_exists(selection):
        return selection
    # Otherwise, look for the first available option
    for m in __MENUS:
        if shutil.which(m):
            return m
    # or default to console.
    return __DEFAULT_MENU


def __menu_gum(
    input: list, title: str, filename: Optional[str] = None, query: Optional[str] = None
):
    raise NotImplementedError


def __menu_fzf(
    input: list, title: str, filename: Optional[str] = None, query: Optional[str] = None
):
    raise NotImplementedError


def __menu_pick(
    data: list, title: str, filename: Optional[str] = None, query: Optional[str] = None
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
    menu = __best_menu(CONFIG.menus)
    if query:
        words = list(filter(lambda w: re.search(r"^\w:", w), shlex.split(query)))
        query = " ".join(words).strip()

    if menu == "gum":
        __menu_gum(data, title, filename, query)
    elif menu == "fzf":
        __menu_fzf(data, title, filename, query)
    else:
        return __menu_pick(data, title, filename, query)
