"""
Tests for download_records.py.
"""
import numpy as np
import shutil
import tempfile
import unittest

from ..download_records import main, parse_args, read_ids


class TestDownloadIds(unittest.TestCase):
    """
    Tests for download_records.py.
    """
    def setUp(self):
        """
        Set up tests.
        """
        self.temp_dir = tempfile.mkdtemp()
        _, self.filename = tempfile.mkstemp(dir=self.temp_dir)

        # write CIDs
        self.cids = [2244]
        _, self.cid_filename = tempfile.mkstemp(suffix='.txt',
                                                dir=self.temp_dir)
        with open(self.cid_filename, 'wb') as f:
            for cid in self.cids:
                f.write('{}\n'.format(cid))

        # write SIDs
        self.sids = [179038559]
        _, self.sid_filename = tempfile.mkstemp(suffix='.txt',
                                                dir=self.temp_dir)
        with open(self.sid_filename, 'wb') as f:
            for sid in self.sids:
                f.write('{}\n'.format(sid))

    def tearDown(self):
        """
        Clean up tests.
        """
        shutil.rmtree(self.temp_dir)

    def run_script(self, ids, args):
        """
        Run main loop of script.
        """
        main(ids, args.output, args.sids, args.download_format,
             args.compression, args.use_3d, args.n_conformers, args.delay)

    def test_read_ids(self):
        """
        Test read_ids.
        """
        ids = read_ids(self.cid_filename)
        assert np.array_equal(ids, self.cids)

    def test_download_cid(self):
        """
        Download a CID.
        """
        ids = read_ids(self.cid_filename)
        args = parse_args([self.cid_filename, self.filename])
        self.run_script(ids, args)
