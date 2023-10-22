# Clipper

A tool for accessing code snippets contained in a folder of plain text Markdown files.
This is a python reimplementation of [snibbets](https://github.com/ttscoff/snibbets)

This is, for the most part, api compatible with `snibbets`. The config file is the same format, the command line arguments are the same (mostly, see below).

For further documentation, reference the snibbets docs (at least until I get around to adding them here).

## Todo List

These are features that `snibbets` has that I have not yet implemented, or 
additional features I'd like to add. They're _very_ roughly in priority order.

* Alfred support
* console colors for terminal output
* better handling of output redirection
* `gum` menus
* `fzf` menus
* `skylighting` highlighting
* Launchbar support (very low priority as I don't use Launchbar)

## Differences from `snibbets`

* pygments highlighting

Pygments is available as a python module, and as such is bundled with clipper. 
This means there's no need to install it separately, and it's always available as
the default highlighter.

* console menu

The default ("console") menu is powered by the [pick](https://github.com/wong2/pick) library.

* Minor formatting differences

I have attempted to maintain compatability for the config file, command-line
options, and snippet files. However, the code is not _exactly_ the same, and I 
have made some opinionated choices around format and whitespace. The result is 
that the output format may differ slightly.

## Ok, but why did I make this?

Honestly? No good reason. Stretching some codeing muscles, learning more about
building and publishing python packages.

Also, I just don't care for ruby and didnt feel like installing it.
