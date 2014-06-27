"""
Tests for PubChem PUG interface.
"""
from pubchem import PubChem


def test_cid():
    """CID request."""
    p = PubChem(delay=3)
    p.get_ids([2244])


def test_sid():
    """SID request."""
    p = PubChem(delay=3)
    p.get_ids([179038559], sids=True)


def test_3d():
    """3D structure request."""
    p = PubChem(delay=3)
    p.get_ids([2244], use_3d=True, n_conformers=10)


def test_aid_cids():
    """Fetch CIDs from AID."""
    p = PubChem()
    p.get_bioassay_ids(466)


def test_aid_sids():
    """Fetch SIDs from AID."""
    p = PubChem()
    p.get_bioassay_ids(466, sids=True)


def test_aid_cids_activity_outcome():
    """Fetch active/inactive CIDs from AID."""
    p = PubChem()
    p.get_bioassay_ids(466, activity_outcome='active')
    p.get_bioassay_ids(466, activity_outcome='inactive')


def test_aid_sids_activity_outcome():
    """Fetch active/inactive SIDs from AID."""
    p = PubChem()
    p.get_bioassay_ids(466, sids=True, activity_outcome='active')
    p.get_bioassay_ids(466, sids=True, activity_outcome='inactive')
