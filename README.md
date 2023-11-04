# Clipper
<img src="docs/sailboat.png">

A tool for accessing code snippets contained in a folder of plain text Markdown files.
This is a python reimplementation of [snibbets](https://github.com/ttscoff/snibbets)

This is, for the most part, api compatible with `snibbets`. The config file is the same format, the command line arguments are identical. There are minor differences, documented below.

For further documentation, reference the snibbets docs (at least until I get around to adding them here).

## Install

Currently only installation from git is supported:

    python -m pip install git+https://github.com/borzilleri/clipper.git

## Todo List

These are features that `snibbets` has that I have not yet implemented, or 
additional features I'd like to add. They're _very_ roughly in priority order.

* Alfred support: IN PROGRESS/Mostly done.

  This should be nearly functionally complete and usable. Remaining tasks are
  improved documentation in the configuration window, and removing "nulls"
  from some of the displayed fields.

* Improved Output Redirection

  Better checking that our output is a tty when prompting for menus.

* Documentation

  Properly document options, usage, installation, etc, here instead of relying
  relying on the snibbets docs.

* Release to PyPi

* `skylighting` highlighter support

  Low priority. `pygments` is built in and works pretty well.

* LaunchBar support
  
  Low priority. I don't use LaunchBar myself, so I'm not as inclined to get this to work.

## Differences from `snibbets`

* `copy` behavior

  When multiple snippets are printed (by specifying `--all` or selecting `All Snippets` from the menu), the entire output will be copied, not just the last snippet's code.

* pygments highlighting

  Pygments is available as a python module, and as such is bundled with clipper. 
  This means there's no need to install it separately, and it's always available as
  the default highlighter.

* console menu

  The default ("console") menu is powered by the [pick](https://github.com/wong2/pick) library.

* Minor formatting differences

  I have attempted to maintain compatability for the config file, command-line options, and snippet files. However, the code is not _exactly_ the same, and I have made some opinionated choices around format and whitespace. The result is that the output format may differ slightly.

## Ok, but why did I make this?

Honestly? No good reason. Stretching some codeing muscles, learning more about
building and publishing python packages.

Also, I just don't care for ruby and didnt feel like installing it.


## Credits & Attribution

<a href="https://www.flaticon.com/free-icons/ship" title="ship icons">Ship icon created by Ahmad Yafie - Flaticon</a>