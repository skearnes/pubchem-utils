"""
Tests for PubChem PUG interface.
"""
from pubchem import pug

aspirin = {'cid': 2244,
           'sid': 179038559,
           'smiles': 'CC(=O)OC1=CC=CC=C1C(=O)O'}


def test_cid():
    """Test CID download."""
    p = pug.PUG(delay=3)
    q = p.get_ids([aspirin['cid']], download_format='smiles', compression=None)
    filename = q.fetch()
    smiles = None
    with open(filename) as f:
        for line in f:
            _, smiles = line.strip().split()
    assert smiles == aspirin['smiles']


def test_sid():
    """Test SID download."""
    p = pug.PUG(delay=3)
    q = p.get_ids([aspirin['sid']], sids=True, download_format='smiles',
                  compression=None)
    filename = q.fetch()
    smiles = None
    with open(filename) as f:
        for line in f:
            _, smiles = line.strip().split()
    assert smiles == aspirin['smiles']
