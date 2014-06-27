"""
Tests for PubChem PUG interface.
"""
from pubchem import pug


def test_cid():
    """Test CID download."""
    p = pug.PUG(delay=3)
    p.get_ids([2244])


def test_sid():
    """Test SID download."""
    p = pug.PUG(delay=3)
    p.get_ids([179038559], sids=True)


def test_3d():
    """Test 3D structure download."""
    p = pug.PUG(delay=3)
    p.get_ids([2244], use_3d=True, n_conformers=10)
