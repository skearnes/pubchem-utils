"""
Tests for PubChem PUG interface.
"""
from cStringIO import StringIO
import gzip
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

    def read_gzip_string(self, string):
        """
        Decompress a gzipped string.

        Parameters
        ----------
        string : str
            Gzipped string.
        """
        with gzip.GzipFile(fileobj=StringIO(string)) as f:
            data = f.read()
        return data

    def test_cid(self):
        """
        2D CID request.
        """
        url = os.path.join(self.rest_url, 'compound/cid/2244/SDF')
        ref = urllib2.urlopen(url).read()
        data = self.engine.get_records([2244])
        assert self.read_gzip_string(data) == ref

    def test_sid(self):
        """
        SID request.
        """
        url = os.path.join(self.rest_url, 'substance/sid/179038559/SDF')
        ref = urllib2.urlopen(url).read()
        data = self.engine.get_records([179038559], sids=True)
        assert self.read_gzip_string(data) == ref

    def test_3d(self):
        """
        3D structure request.
        """
        url = os.path.join(self.rest_url,
                           'compound/cid/2244/SDF?record_type=3d')
        ref = urllib2.urlopen(url).read()
        data = self.engine.get_records([2244], use_3d=True)
        assert self.read_gzip_string(data) == ref

    def test_aid_cids(self):
        """
        Fetch CIDs from an AID.
        """
        url = os.path.join(self.rest_url, 'assay/aid/466/cids/TXT')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_bioassay_ids(466)
        assert np.array_equal(data, ref)

    def test_aid_sids(self):
        """
        Fetch SIDs from an AID.
        """
        url = os.path.join(self.rest_url, 'assay/aid/466/sids/TXT')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_bioassay_ids(466, sids=True)
        assert np.array_equal(data, ref)

    def test_aid_active_cids(self):
        """
        Fetch active CIDs from an AID.
        """
        url = os.path.join(self.rest_url,
                           'assay/aid/466/cids/TXT?cids_type=active')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_bioassay_ids(466, activity_outcome='active')
        assert np.array_equal(data, ref)

    def test_aid_inactive_cids(self):
        """
        Fetch inactive CIDs from an AID.
        """
        url = os.path.join(self.rest_url,
                           'assay/aid/466/cids/TXT?cids_type=inactive')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_bioassay_ids(466, activity_outcome='inactive')
        assert np.array_equal(data, ref)

    def test_aid_active_sids(self):
        """
        Fetch active SIDs from an AID.
        """
        url = os.path.join(self.rest_url,
                           'assay/aid/466/sids/TXT?sids_type=active')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_bioassay_ids(466, sids=True,
                                            activity_outcome='active')
        assert np.array_equal(data, ref)

    def test_aid_inactive_sids(self):
        """
        Fetch inactive SIDs from an AID.
        """
        url = os.path.join(self.rest_url,
                           'assay/aid/466/sids/TXT?sids_type=inactive')
        ref = np.asarray(urllib2.urlopen(url).read().split(), dtype=int)
        data = self.engine.get_bioassay_ids(466, sids=True,
                                            activity_outcome='inactive')
        assert np.array_equal(data, ref)
