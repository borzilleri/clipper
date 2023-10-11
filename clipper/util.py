from pathlib import Path
from typing import Optional, List
import os
import platform
import pyperclip
import re
import shutil
import subprocess
import sys

MACOS_APP_DIRS = ["/Applications", "/Applications/Setapp", "~/Applications"]
EDITORS = ["code", "subl", "nano", "vim"]


def get_app_path(cmd: str) -> Optional[str]:
    app = Path(re.sub(r"(\\.app)?$", ".app", cmd)).expanduser().absolute()
    command = (
        cmd if Path(cmd).expanduser().absolute() == cmd else re.sub(r"\\.app$", "", cmd)
    )
    if app.exists():
        return command
    for dir in MACOS_APP_DIRS:
        if (Path(dir) / app).exists():
            return command
    return None


def is_bundle(cmd: str) -> bool:
    return re.search(r"""^\w+(\.\w+){2,}""", cmd) is not None


def darwin_cmd(path: str, app: Optional[str]):
    if app is None:
        return ["open", path]
    elif is_bundle(app):
        return ["open", "-b", app, path]
    elif get_app_path(app):
        return ["open", "-a", app, path]
    else:
        return [app, path]


def windows_cmd(path: str, app: Optional[str]):
    if app:
        return [app, path]
    return ["start", path]


def linux_cmd(path: str):
    if shutil.which("xdg-open"):
        return ["xdg-open", path]
    else:
        raise FileNotFoundError("Unable to determine executable for `xdg-open`.")


def open_file(path: str, app: Optional[str] = None):
    system = platform.system()
    if system == "Darwin":
        cmd = darwin_cmd(path, app)
    elif system == "Windows":
        cmd = windows_cmd(path, app)
    else:
        cmd = linux_cmd(path)
    subprocess.Popen(cmd).wait()


def copy(text: str):
    pyperclip.copy(text)


def paste() -> str:
    return pyperclip.paste()


def best_editor():
    if os.getenv("EDITOR"):
        return os.getenv("EDITOR")
    if os.getenv("EDITOR"):
        return os.getenv("GIT_EDITOR")
    for editor in EDITORS:
        editor_path = shutil.which(editor)
        if editor_path:
            return editor_path
    return None


def trim_list(l: List[str]) -> list:
    start_idx = 0
    skip = True
    for item in l:
        if len(item.strip()) == 0 and skip:
            start_idx += 1
        else:
            skip = False
    end_idx = len(l)
    skip = True
    for i in range(len(l)):
        idx = len(l) - i - 1
        if len(l[idx].strip()) == 0 and skip:
            end_idx -= 1
        else:
            skip = False
    return l[start_idx:end_idx]


def strip_empty_lines(val: str):
    return "\n".join(trim_list(val.split("\n")))


def warn(s: str):
    print(s, file=sys.stderr)


def is_fenced(s: str) -> bool:
    count = len(re.findall(r"^```", s, flags=re.M))
    return count > 1 and (count % 2) == 0

def get_fences(text: str):
    if not is_fenced(text):
        return []
    p = re.compile(r"^(?:`{3,})(?P<lang> *\S+)? *\n(?P<code>[\s\S]*?)\n(?:`{3,}) *(?=\n|\Z)", flags=re.M | re.I)
    fences = []
    for m in p.finditer(text):
        fences.append(m.groupdict())
    return fences
