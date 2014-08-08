"""
Download records from PubChem by ID.
"""

__author__ = "Steven Kearnes"
__copyright__ = "Copyright 2014, Stanford University"
__license__ = "3-clause BSD"

import argparse
import numpy as np

from pubchem_utils import PubChem


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
    parser.add_argument('output',
                        help='Output filename.')
    parser.add_argument('--sids', action='store_true',
                        help='Whether IDs are substance IDs (if False, IDs ' +
                             'are assumed to be compound IDs).')
    parser.add_argument('-f', '--format', dest='download_format',
                        default='sdf', help='Download format.')
    parser.add_argument('-c', '--compression', default='gzip',
                        help='Compression type.')
    parser.add_argument('--3d', action='store_true', dest='use_3d',
                        help='Whether to download 3D structures.')
    parser.add_argument('-n', '--n-conformers', type=int, default=1,
                        help='Number of conformers to download if ' +
                             'retrieving 3D structures.')
    parser.add_argument('-d', '--delay', type=int, default=10,
                        help='Number of seconds to wait between status ' +
                             'checks.')
    rval = parser.parse_args(input_args)
    return rval


def main(ids, filename=None, sids=False, download_format='sdf',
         compression='gzip', use_3d=False, n_conformers=1, delay=10):
    """
    Download records from PubChem by ID.

    Parameters
    ----------
    ids : iterable
        PubChem substance or compound IDs.
    filename : str, optional
        Output filename. If not provided, a temporary file is created.
    sids : bool, optional (default False)
        Whether ids are SIDs. If False, IDs are assumed to be CIDs.
    download_format : str, optional (default 'sdf')
        Download file format.
    compression : str, optional (default 'gzip')
        Compression type for downloaded structures.
    use_3d : bool, optional (default True)
        Whether to query 3D information. If False, 2D information is
        retrieved.
    n_conformers : int, optional (default 1)
        Number of conformers to download if retrieving 3D structures.
    delay : int, optional (default 10)
        Number of seconds to wait between status checks.
    """
    engine = PubChem(delay=delay)
    engine.get_records(ids, filename, sids, download_format, compression,
                       use_3d, n_conformers)


def read_ids(filename):
    """
    Read record IDs from a file.

    Parameters
    ----------
    filename : str
        Filename containing PubChem record IDs.
    """
    with open(filename) as f:
        ids = np.asarray([line.strip() for line in f], dtype=int)
    return ids

if __name__ == '__main__':
    args = parse_args()
    record_ids = read_ids(args.input)
    main(record_ids, args.output, args.sids, args.download_format,
         args.compression, args.use_3d, args.n_conformers, args.delay)
