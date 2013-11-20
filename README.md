# Purpose

`beastcommentparser` extracts and formats data from BEAST summary trees for use in downstream analyses.

# Dependencies

* Python 2.7
* [DendroPy](http://packages.python.org/DendroPy)

# Installation

## OS X

The simplest way is to use [Homebrew](http://brew.sh). With Homebrew:

```sh
brew install python
pip install dendropy
pip install -e git+https://github.com/jonchang/beastcommentparser.git#egg=beastcommentparser
```

# Usage

An example BEAST summary tree, `arctoid.tree`, is included in the `examples/` directory.

```sh
bcp.py examples/arctoid.tree
#=> Output written to arctoid.txt
```

Running the program with only a tree as the argument will create a text file of the same name in the current directory. You can then view this file in a spreadsheet program or analzyze it further in R, Python, etc.

Only report on leaf nodes:

```sh
bcp.py --report=leaf examples/arctoid.tree
```

For more options, consult the help:

```sh
python bcp.py --help
```

There is also preliminary support for summary trees from phylogeographic analyses.

