#!/usr/bin/env python

"""bcp.py - extracts comment data from BEAST summary trees"""

import sys
import argparse
import csv
import os.path
import dendropy
from beastcommentparser import BeastCommentParser



def get_args():
    parser = argparse.ArgumentParser(description="extracts comment data from" +
        " BEAST summary trees")
    parser.add_argument('tree', metavar="FILE", help="tree files to process",
        nargs="+")

    parser.add_argument('-o', '--output', help="output file")
    parser.add_argument('--format', default="nexus", help="tree format",
        choices=["nexus", "newick", "fasta", "phylip"])
    parser.add_argument('--data-type', help="type of character data " +
        "(required for fasta and phylip)", choices=("dna rna protein " +
        "standard restriction infinite").split())
    parser.add_argument('-r', '--report', action="store", default="all",
        choices=["leaf", "internal", "all"], help="which types of nodes to " +
        "extract data from")
    parser.add_argument('-v', '--values', action="store", default="ALL",
        help="comma-separated list of values to report (e.g., height)")

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
                            table.add(value, name, "{0}{1}={2}".format(
                                set_name, item_value, key))
        self.merge(table)


def iterate_nodes(tree, nodes, columns, all=False, use_table=None):

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
    """Returns the two farthest leaf nodes that have the given node
    as a most recent common ancestor.
    """
    nodes = list(head.leaf_iter())
    for node in nodes:
        for bnode in reversed(nodes):
            if node == bnode:
                continue  # no need to check this case
            common = tree.mrca(taxa=[node.taxon, bnode.taxon])
            if head == common:
                return node, bnode


def main():
    args = get_args()

    all_values = True if args.values == 'ALL' else False
    choice = args.values.split(',')

    for treefile in args.tree:
        tree = dendropy.Tree.get_from_path(treefile, args.format)
        taxon_namespace = tree.taxon_namespace
        # In order to "encode_splits" we need to have a prepopulated TaxonSet
        # object. It costs a little bit to parse the tree twice but that's OK.
        tree = dendropy.Tree.get_from_path(treefile, args.format,
            taxon_namespace=taxon_namespace)
        tree.encode_bipartitions()
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
            table = iterate_nodes(tree, tree.leaf_node_iter(), choice,
                all_values, use_table=table)
        if args.report == "internal" or args.report == "all":
            table = iterate_nodes(tree, tree.internal_nodes(), choice,
                all_values, use_table=table)
        rows = table.output()

        if args.output:
            outfile = args.output
        else:
            root, ext = os.path.splitext(os.path.basename(treefile))
            outfile = root + ".txt"
        with open(outfile, "wb") as wfile:
            writer = csv.writer(wfile, 'excel-tab')
            writer.writerows(rows)
            print "Output written to {0}".format(outfile)

if __name__ == '__main__':
    main()
