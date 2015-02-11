"""
Scripting utilities.
"""
import gzip

__author__ = "Steven Kearnes"
__copyright__ = "Copyright 2014, Stanford University"
__license__ = "3-clause BSD"


def read_ids(filename):
    """
    Read record IDs from a file.

    Parameters
    ----------
    filename : str
        Filename containing record IDs.
    """
    if filename.endswith('.gz'):
        f = gzip.open(filename)
    else:
        f = open(filename)
    ids = [line.strip() for line in f]
    f.close()
    return ids
