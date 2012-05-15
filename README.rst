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

Install dendropy, using `pip <http://pypi.python.org/pypi/pip>`_::

    pip install dendropy

Install beastcommentparser::

    git clone https://jonchang@github.com/jonchang/beastcommentparser.git
    cd beastcommentparser/
    pip install .

Usage
*****

An example BEAST summary tree, *arctoid.tree*, is included in the examples/ directory. The default settings will report all the data contained in the file::

    python bcp.py examples/arctoid.tree

An output file *arctoid.txt* will be created in the current directory. It is then possible to view this in Microsoft Excel or other spreadsheet software.

Reporting only leaf nodes::

    python bcp.py --report=leaf examples/arctoid.tree

More options can be found viewing the help::

    python bcp.py --help

Results from phylogeographic analyses are also extracted and formatted nicely, but this feature is not well-tested.

See also
********

- `BEAST <http://beast.bio.ed.ac.uk/>`_
- `dendropy <http://packages.python.org/DendroPy>`_
