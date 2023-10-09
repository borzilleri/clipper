# Clipper

A tool for accessing code snippets contained in a folder of plain text Markdown files.
This is a python reimplementation of [snibbets](https://github.com/ttscoff/snibbets)

This is, for the most part, api compatible with `snibbets`. The config file is the same format, the command line arguments are the same (mostly, see below).

For further documentation, reference the snibbets docs (at least until I get around to adding them here).

## Todo List

* pygments highlighting
* `gum` menus
* `fzf` menus
* `skylighting` highlighting
* Launchbar support
* Alfred support

## Differences from `snibbets`

* pygments highlighting

Pygments is available as a python module, and as such is bundled with clipper. This doesn't change the behavior, but installing pygments separately is no longer required.

* console menu

The default ("console") menu is powered by the [pick](https://github.com/wong2/pick) library.