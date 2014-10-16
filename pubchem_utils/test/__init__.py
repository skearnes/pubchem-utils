"""
Tests for PubChem PUG interface.
"""
import numpy as np
import os
import unittest
import urllib2

from .. import PubChem


class TestPubChem(unittest.TestCase):
    """
    Tests for PubChem.

    Reference comparisons are made when possible to records retrieved using the
    PubChem PUG REST interface via http://pubchem.ncbi.nlm.nih.gov/rest/pug.
    """
    def setUp(self):
        """
        Set up tests.
        """
        self.engine = PubChem(delay=3)  # shorten delay for tests
        self.rest_url = 'http://pubchem.ncbi.nlm.nih.gov/rest/pug'

    def identical_sdf(self, a, b):
        """
        Compare SDF records.

        SDF records downloaded from PubChem have a timestamp that should not be
        considered in the comparison.

        Parameters
        ----------
        a, b : str
            SDF records to compare.
        """
        if a == b:  # sometimes the timestamps match
            return True

        try:
            a_lines = a.split('\n')
            b_lines = b.split('\n')
            assert len(a_lines) == len(b_lines)
            for i in xrange(len(a_lines)):
                if i == 1:
                    assert a_lines[i].strip().startswith('-OEChem')
                    assert b_lines[i].strip().startswith('-OEChem')
                    continue
                assert a_lines[i] == b_lines[i]
            return True
        except AssertionError:
            return False

    def test_cid(self):
        """
        2D CID request.
        """
        url = os.path.join(self.rest_url, 'compound/cid/2244/SDF')
        ref = urllib2.urlopen(url).read()
        data = self.engine.get_records([2244])
        assert self.identical_sdf(data, ref)

    def test_sid(self):
        """
        SID request.
        """
        url = os.path.join(self.rest_url, 'substance/sid/179038559/SDF')
        ref = urllib2.urlopen(url).read()
        data = self.engine.get_records([179038559], sids=True)
        assert self.identical_sdf(data, ref)

    def test_3d(self):
        """
        3D structure request.
        """
        url = os.path.join(self.rest_url,
                           'compound/cid/2244/SDF?record_type=3d')
        ref = urllib2.urlopen(url).read()
        data = self.engine.get_records([2244], use_3d=True)
        assert self.identical_sdf(data, ref)

    def test_aid_cids(self):
        """
        Fetch CIDs from an AID.
        """
        url = os.path.join(self.rest_url, 'assay/aid/466/cids/TXT')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_ids_from_assay(466)
        assert np.array_equal(data, ref)

    def test_aid_sids(self):
        """
        Fetch SIDs from an AID.
        """
        url = os.path.join(self.rest_url, 'assay/aid/466/sids/TXT')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_ids_from_assay(466, sids=True)
        assert np.array_equal(data, ref)

    def test_aid_active_cids(self):
        """
        Fetch active CIDs from an AID.
        """
        url = os.path.join(self.rest_url,
                           'assay/aid/466/cids/TXT?cids_type=active')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_ids_from_assay(466, activity_outcome='active')
        assert np.array_equal(data, ref)

    def test_aid_inactive_cids(self):
        """
        Fetch inactive CIDs from an AID.
        """
        url = os.path.join(self.rest_url,
                           'assay/aid/466/cids/TXT?cids_type=inactive')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_ids_from_assay(466, activity_outcome='inactive')
        assert np.array_equal(data, ref)

    def test_aid_active_sids(self):
        """
        Fetch active SIDs from an AID.
        """
        url = os.path.join(self.rest_url,
                           'assay/aid/466/sids/TXT?sids_type=active')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_ids_from_assay(466, sids=True,
                                              activity_outcome='active')
        assert np.array_equal(data, ref)

    def test_aid_inactive_sids(self):
        """
        Fetch inactive SIDs from an AID.
        """
        url = os.path.join(self.rest_url,
                           'assay/aid/466/sids/TXT?sids_type=inactive')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_ids_from_assay(466, sids=True,
                                              activity_outcome='inactive')
        assert np.array_equal(data, ref)

    def test_get_assay_data(self):
        """
        Test PubChem.get_assay_data.
        """
        data = self.engine.get_assay_data(504772)
        assert len(data.splitlines()) == 332  # 331 records plus header

    def test_id_exchange(self):
        """
        Test PubChem.id_exchange.
        """
        data = self.engine.id_exchange('CHEMBL25')
        assert data['CHEMBL25'] == 2244

    def test_structure_search_smiles(self):
        """
        Test PubChem.structure_search with SMILES queries.
        """
        smiles = self.engine.get_records([2244], download_format='smiles')
        smiles = smiles.split()[1]
        assert self.engine.structure_search(smiles) == 2244

    def test_structure_search_sdf(self):
        """
        Test PubChem.structure_search with SDF queries.
        """
        sdf = self.engine.get_records([2244])
        assert self.engine.structure_search(
            sdf, structure_format='sdf') == 2244

    def test_get_parent_cids(self):
        """
        Test PubChem.get_parent_cids.
        """
        same = self.engine.get_parent_cids([2244])
        assert same == {2244}, same
        parents = self.engine.get_parent_cids([23666729, 5338317])
        assert parents == {2244, 3672}, parents
