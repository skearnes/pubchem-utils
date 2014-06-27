"""
Tests for PubChem PUG interface.
"""
from pubchem import pug


def test_cid():
    """Test CID request."""
    p = pug.PUG(delay=3)
    p.get_ids([2244])


def test_sid():
    """Test SID request."""
    p = pug.PUG(delay=3)
    p.get_ids([179038559], sids=True)


def test_3d():
    """Test 3D structure request."""
    p = pug.PUG(delay=3)
    p.get_ids([2244], use_3d=True, n_conformers=10)