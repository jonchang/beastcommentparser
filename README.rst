Purpose
*******

*beastcommentparser* is a program to retrieve annotations from BEAST summary trees.

Dependencies
************

- Python 2.7
- dendropy

Installation
************

Ensure Python 2.7 is installed::

    python -V

Install dendropy::

    pip install dendropy

Install beastcommentparser::

    git clone git@github.com:jonchang/beastcommentparser.git

Testing
*******

In the program's directory::

    python BeastCommentParser/__init__.py -v

At the bottom of all the output you should see "Test passed."

Usage
*****

An example BEAST summary tree, *arctoid.tree*, is included in the examples/ directory. The default settings will report all the data contained in the file::

    python bcp.py examples/arctoid.tree

Write to a file instead, reporting only leaf nodes::

    python bcp.py --report=leaf --output=arctoid.txt examples/arctoid.tree

More options can be found viewing the help::

    python bcp.py --help

See also
********

- BEAST <http://beast.bio.ed.ac.uk/>
- dendropy <http://packages.python.org/DendroPy>
