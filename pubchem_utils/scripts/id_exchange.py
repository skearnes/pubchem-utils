#!/usr/bin/env python
"""
Use the PubChem Identifier Exchange service.
"""
import argparse
import numpy as np

from pubchem_utils import PubChem
from pubchem_utils.scripts import read_ids

__author__ = "Steven Kearnes"
__copyright__ = "Copyright 2014, Stanford University"
__license__ = "3-clause BSD"


def parse_args(input_args=None):
    """
    Parse command-line arguments.

    Parameters
    ----------
    input_args : list, optional
        Input arguments. If not provided, defaults to sys.argv[1:].
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                        help='Input filename containing record IDs.')
    parser.add_argument('-s', '--source',
                        help='Source for input IDs. If not provided, the ' +
                             'source will be inferred from the input IDs.')
    parser.add_argument('-m', '--mapping', action='store_true',
                        help='Whether to write ID mapping. If false, only ' +
                             'result IDs will be saved.')
    parser.add_argument('-p', '--prefix',
                        help='Prefix for output files.')
    parser.add_argument('--sids', action='store_true',
                        help='Whether returned IDs are substance IDs '
                             '(if False, returned IDs will be compound IDs).')
    parser.add_argument('-d', '--delay', type=int, default=10,
                        help='Number of seconds to wait between status ' +
                             'checks.')
    return parser.parse_args(input_args)


def main(ids, source=None, prefix=None, sids=False, mapping=False, delay=10):
    """
    Download records from PubChem by ID.

    Parameters
    ----------
    ids : iterable
        Source IDs.
    source : str, optional
        Input source. If None, it will be inferred from ids (if possible).
    prefix : str, optional
        Prefix for output files.
    sids : bool, optional (default False)
        Whether ids are SIDs. If False, IDs are assumed to be CIDs.
    mapping : bool, optional (default False)
    delay : int, optional (default 10)
        Number of seconds to wait between status checks.
    """
    engine = PubChem(delay=delay)
    if sids:
        output_type = 'sid'
    else:
        output_type = 'cid'
    matched, unmatched = engine.id_exchange(np.unique(ids), source,
                                            output_type=output_type)
    if mapping:
        with open('{}-mapping.txt'.format(prefix), 'wb') as f:
            for key, value in matched.items():
                f.write('{}\t{}\n'.format(key, value))
    else:
        with open('{}-matched.txt'.format(prefix), 'wb') as f:
            for value in matched.values():
                f.write('{}\n'.format(value))
    if len(unmatched):
        with open('{}-unmatched.txt'.format(prefix), 'wb') as f:
            for value in unmatched:
                f.write('{}\n'.format(value))

if __name__ == '__main__':
    args = parse_args()
    record_ids = read_ids(args.input)
    main(record_ids, args.source, args.prefix, args.sids, args.mapping,
         args.delay)
