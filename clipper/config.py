from argparse import Namespace
from enum import Enum
from pathlib import Path
from typing import Optional
import yaml

# To maintain compatibility with the original `snibbets` tool,
# we use the same config file.
CONFIG_DIR = Path("~/.config/snibbets").expanduser().absolute()
CONFIG_FILE = CONFIG_DIR / "snibbets.yml"

DEFAULT_SOURCE_PATH = "~/Dropbox/Snippets"

Format = Enum("Format", ["raw", "json", "alfred"])


class Options:
    save_config: bool = False
    edit_config: bool = False
    edit_snippet: bool = False
    paste_snippet: bool = False

    def __init__(self) -> None:
        self.save_config = self.save_config
        self.edit_config = self.edit_config
        self.edit_snippet = self.edit_snippet
        self.paste_snippet = self.paste_snippet

    def parse_args(self, args: Namespace) -> None:
        self.save_config = args.save
        self.edit_config = args.configure
        self.edit_snippet = args.edit
        self.paste_snippet = args.paste


class Configuration:
    all: bool = False
    all_notes: bool = False
    copy: bool = False
    highlight: bool = False
    include_blockquotes: bool = False
    name_only: bool = False
    output: str = Format.raw.name
    source: Path = Path(DEFAULT_SOURCE_PATH).expanduser().absolute()

    extension: str = "md"
    highlighter: Optional[str] = None
    highlight_theme: Optional[str] = "monokai"
    editor: Optional[str] = "TextEdit"
    interactive: bool = True
    menus: Optional[str] = "console"

    format: Format = Format[output]

    def __init__(self) -> None:
        pass

    def from_dict(self, data: dict) -> None:
        # If not configured, use the default value.
        self.all = data.get("all", self.all)
        self.all_notes = data.get("all_notes", self.all_notes)
        self.copy = data.get("copy", self.copy)
        self.highlight = data.get("highlight", self.highlight)
        self.include_blockquotes = data.get(
            "include_blockquotes", self.include_blockquotes
        )
        self.name_only = data.get("name_only", self.name_only)
        self.output = data.get("output", self.output)
        self.source = (
            Path(data.get("source", DEFAULT_SOURCE_PATH)).expanduser().absolute()
        )

        # Other configs
        self.extension = data.get("extension", self.extension)
        self.highlighter = data.get("highlighter", self.highlighter)
        self.highlight_theme = data.get("highlight_theme", self.highlight_theme)
        self.editor = data.get("editor", self.editor)
        self.interactive = data.get("interactive", self.interactive)
        self.menus = data.get("menus", self.menus)

        self.format = Format[self.output]

    def to_dict(self) -> dict:
        return {
            "all": self.all,
            "all_notes": self.all_notes,
            "copy": self.copy,
            "editor": self.editor,
            "extension": self.extension,
            "highlight": self.highlight,
            "highlighter": self.highlighter,
            "highlihgt_theme": self.highlight_theme,
            "include_blockquotes": self.include_blockquotes,
            "interactive": self.interactive,
            "name_only": self.name_only,
            "output": self.output,
            "source": str(self.source),
            "menus": self.menus,
        }

    def update_from_args(self, args: Namespace):
        if args.all:
            self.all = args.all
        if args.notes is not None:
            self.all_notes = args.notes
        if args.copy is not None:
            self.copy = args.copy
        if args.name_only is not None:
            self.name_only = args.name_only
        if args.output is not None:
            self.output = args.output.lower()
            self.format = Format[self.output]
        if args.source is not None:
            self.source = Path(args.source).expanduser().absolute()
        if args.blockquotes is not None:
            self.include_blockquotes = args.blockquotes
        if args.highlight is not None:
            self.highlight = args.highlight

        if args.quiet:
            self.interactive = False

        if self.format == Format.alfred:
            self.all = True
            self.interactive = False

    def read_config(self) -> None:
        if CONFIG_FILE.exists():
            with CONFIG_FILE.open() as f:
                data = yaml.safe_load(f)
                self.from_dict(data)

    def write_config(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(self.to_dict(), f)


CONFIG = Configuration()
OPTIONS = Options()
