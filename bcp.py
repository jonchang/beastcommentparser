#!/usr/bin/env python

"""bcp.py - dumps comment data from BEAST trees in a format suitable for consumption by more advanced spreadsheet programs.
"""

import sys

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description="extracts comment data from BEAST trees to a format suitable for consumption by more advanced spreadsheet programs.")
    parser.add_argument('tree', metavar="FILE", help="tree file(s) to process", nargs="+")

    parser.add_argument('-o', '--output', metavar="OUTPUT", type=argparse.FileType(mode='w', bufsize=1), default=sys.stdout, help="""write output to %(metavar)s. (default: stdout)""")
    parser.add_argument('-f', '--format', choices=["csv", "tsv"], default="tsv", help="""type of output. (default: %(default)s)""")
    parser.add_argument('--schema', default="nexus", help="""specify schema of FILE. (default: %(default)s).""", choices=["nexus", "newick", "fasta", "phylip"])
    parser.add_argument('--data-type', help="""required if SCHEMA is fasta or phylip.""", choices=["dna", "rna", "protein", "standard", "restriction", "infinite"])
    parser.add_argument('-r', '--report', action="store", default="all", choices=["leaf", "internal", "all"], help="""which types of nodes to report (default: %(default)s)""")
    parser.add_argument('-v', '--values', action="store", default="ALL", help="""comma-separated list of values to report (default: %(default)s).""") 

    args = parser.parse_args()
    return args

class Table:
    def __init__(self):
        from collections import defaultdict
        self.data = defaultdict(dict)
        self.cols = set()

    def add(self, data, row_name, col_name):
        self.data[row_name][col_name] = data
        self.cols.add(col_name)

    def add_row_dict(self, new_dict, row_name):
        self.data[row_name] = dict(self.data[row_name], **new_dict)
        new_cols = set(new_dict.keys())
        self.cols.update(new_cols)

    def output(self, not_available=None):
        sorted_cols = sorted(self.cols)
        header = ['Row label']
        header.extend(sorted_cols)
        yield header
        for name, row in sorted(self.data.iteritems()):
            output = [name]
            for x in sorted_cols:
                try:
                    output.append(row[x])
                except KeyError:
                    output.append(not_available)
            yield output

    def merge(self, other):
        for name, row in other.data.iteritems():
            self.add_row_dict(row, name)

    def transform_set(self):
        import re
        from collections import defaultdict

        capture = re.compile('(.+\.set)\[\d+\]')

        set_keys = defaultdict(list)
        for col in self.cols:
            matched = capture.match(col)
            if matched:
                set_keys[matched.group(1)].append(matched.group(0))

        table = Table()

        for set_name, set_items in set_keys.iteritems():
            set_values = set()
            for col in self.cols:
                matched = re.match("{0}(\.\w+)\[\d+\]$".format(set_name), col)
                if matched:
                    set_values.add(matched.group(1))

            for name, row in self.data.iteritems():
                for item in set_items:
                    index = re.search('\[\d+\]$', item).group(0)
                    try:
                        key = row[item]
                    except KeyError:
                        continue
                    for item_value in set_values:
                        value = row[set_name + item_value + index]
                        if value:
                            table.add(value, name, "{0}{1}={2}".format(set_name, item_value, key))
        self.merge(table)


def iterate_nodes(tree, nodes, columns, all=False, use_table=None):
    from BeastCommentParser import BeastCommentParser

    if use_table:
        table = use_table
    else:
        table = Table()

    for node in nodes:
        rowname = ''
        if 'taxon' in dir(node) and 'label' in dir(node.taxon):
            rowname = node.taxon.label
        else:
            n1, n2 = reverse_mrca(tree, node)
            rowname = "MRCA of %s and %s" % (n1.taxon.label, n2.taxon.label)

        if 'age' in dir(node):
            table.add(node.age, rowname, 'age')

        if len(node.comments):
            data = BeastCommentParser(node.comments[0]).parse()

            if all:
                columns = data.keys()
            for k in columns:
                if isinstance(data[k], basestring):
                    table.add(data[k], rowname, k)
                else:
                    try:
                        for num, value in enumerate(data[k]):
                            table.add(value, rowname, k + '[{0}]'.format(num))
                    except TypeError:
                        table.add(data[k], rowname, k)
    return table

def reverse_mrca(tree, head):
    """Returns the two farthest leaf nodes that have the provided node as a most recent common ancestor.
    """
    nodes = list(head.leaf_iter())
    for node in nodes:
        for bnode in reversed(nodes):
            if node == bnode:
                continue # no need to check this case
            common = tree.mrca(taxa=[node.taxon, bnode.taxon])
            if head == common:
                return node, bnode

def main():
    import dendropy
    import csv

    args = get_args()

    all_values = False
    if args.values == 'ALL':
        all_values = True
    choice = args.values.split(',')

    for treefile in args.tree:
        tree = dendropy.Tree.get_from_path(treefile, args.schema)
        taxon_set = tree.taxon_set
        # In order to "encode_splits" we need to have a prepopulated TaxonSet
        # object. It costs a little bit to parse the tree twice but that's OK.
        tree = dendropy.Tree.get_from_path(treefile, args.schema, taxon_set=taxon_set, encode_splits=True)
        tree.ladderize()

        if all_values:
            try:
                tree.calc_node_ages()
            except ValueError:
                print "WARNING: {0} is not ultrametric".format(treefile)
                print "Rooted: {0}".format(tree.is_rooted)
                tree.calc_node_ages(check_prec=False)

        table = Table()
        if args.report == "leaf" or args.report == "all":
            table = iterate_nodes(tree, tree.leaf_iter(), choice, all_values, use_table=table)
        if args.report == "internal" or args.report == "all":
            table = iterate_nodes(tree, tree.internal_nodes(), choice, all_values, use_table=table)
        rows = table.output()

        if args.format == 'tsv':
            writer = csv.writer(args.output, 'excel-tab')
            writer.writerows(rows)
        else:
            writer = csv.writer(args.output, 'excel')
            writer.writerows(rows)

if __name__ == '__main__':
    main()
