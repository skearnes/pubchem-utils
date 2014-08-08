"""
Utilities for interacting with PubChem.
"""

__author__ = "Steven Kearnes"
__copyright__ = "Copyright 2014, Stanford University"
__license__ = "3-clause BSD"

import numpy as np
import urllib2

from .pug import PUGQuery


class PubChem(object):
    """
    Submit queries to PUG and return PUGQuery objects.

    Parameters
    ----------
    submit : bool, optional (default True)
        Whether to automatically submit PUGQuery queries.
    delay : int, optional (default 10)
        Number of seconds for PUGQuery objects to wait between status
        checks.
    """
    def __init__(self, submit=True, delay=10):
        self.submit = submit
        self.delay = delay

    def get_records(self, ids, filename=None, sids=False, download_format='sdf',
                    compression='gzip', use_3d=False, n_conformers=1):
        """
        Download records for substances or compounds identified by
        PubChem substance IDs (SIDs) or compound IDs (CIDs).

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
        """
        query_template = """
        <PCT-Data>
         <PCT-Data_input>
          <PCT-InputData>
           <PCT-InputData_download>
            <PCT-Download>
             <PCT-Download_uids>
              <PCT-QueryUids>
               <PCT-QueryUids_ids>
                <PCT-ID-List>
                 <PCT-ID-List_db>%(database)s</PCT-ID-List_db>
                 <PCT-ID-List_uids>
                  %(uids)s
                 </PCT-ID-List_uids>
                </PCT-ID-List>
               </PCT-QueryUids_ids>
              </PCT-QueryUids>
             </PCT-Download_uids>
             <PCT-Download_format value="%(download_format)s"/>
             <PCT-Download_compression value="%(compression)s"/>
             <PCT-Download_use-3d value="%(use_3d)s"/>
             <PCT-Download_n-3d-conformers>
              %(n_conformers)s
             </PCT-Download_n-3d-conformers>
            </PCT-Download>
           </PCT-InputData_download>
          </PCT-InputData>
         </PCT-Data_input>
        </PCT-Data>
        """
        mapping = {}

        # database
        if sids:
            mapping['database'] = 'pcsubstance'
        else:
            mapping['database'] = 'pccompound'

        # download format
        download_formats = ['text-asn', 'binary-asn', 'xml', 'sdf', 'image',
                            'image-small', 'smiles', 'inchi']
        assert download_format in download_formats, (
            'download_format must be one of ' + str(download_formats))
        mapping['download_format'] = download_format

        # compression
        if compression is None:
            compression = 'none'
        compressions = ['none', 'gzip', 'bzip2']
        assert compression in compressions, (
            'compression must be one of ' + str(compressions))
        mapping['compression'] = compression

        # 3D
        if use_3d:
            mapping['use_3d'] = 'true'
        else:
            mapping['use_3d'] = 'false'

        # conformers
        mapping['n_conformers'] = n_conformers

        # create XML for each ID
        xml_uids = ''
        for uid in ids:
            xml_uids += ('<PCT-ID-List_uids_E>{}'.format(uid) +
                         '</PCT-ID-List_uids_E>\n')
        mapping['uids'] = xml_uids

        # construct query
        query = PUGQuery(query_template % mapping, submit=self.submit,
                         delay=self.delay)
        rval = query.fetch(filename)
        return rval

    def get_ids_from_assay(self, aid, sids=False, activity_outcome=None):
        """
        Retrieve substance or compound IDs tested in a PubChem BioAssay
        assay.

        Parameters
        ----------
        aid : int
            PubChem BioAssay assay ID (AID).
        sids : bool, optional (default False)
            Whether ids are SIDs. If False, IDs are assumed to be CIDs.
        activity_outcome : str, optional
            If provided, only retrieve records with this activity outcome,
            such as 'active'.
        """
        url_template = ('https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid' +
                        '/%(aid)s/%(database)s/txt')
        mapping = {'aid': aid}
        if sids:
            mapping['database'] = 'sids'
        else:
            mapping['database'] = 'cids'
        if activity_outcome is not None:
            url_template += '?{}_type={}'.format(mapping['database'],
                                                 activity_outcome.lower())
        url = url_template % mapping
        response = urllib2.urlopen(url)
        ids = []
        for this in response.readlines():
            this = this.strip()
            if this:
                ids.append(this)
        ids = np.asarray(ids, dtype=int)
        return ids
