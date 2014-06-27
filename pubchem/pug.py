"""
Utilities for interacting with the PubChem Power User Gateway (PUG).

The PUG XML schema is located at
https://pubchem.ncbi.nlm.nih.gov/pug/pug.xsd.

See also https://pubchem.ncbi.nlm.nih.gov/pug/pughelp.html.
"""

__author__ = "Steven Kearnes"
__copyright__ = "Copyright 2014, Stanford University"
__license__ = "BSD 3-clause"

import re
import time
import urllib
import urllib2
import warnings


class PUG(object):
    """
    Submit queries to PUG and return PUGQuery objects.

    Parameters
    ----------
    submit : bool, optional (default True)
        Whether to automatically submit each query.
    delay : int, optional (default 10)
        Number of seconds for PUGQuery objects to wait between status
        checks.
    """
    def __init__(self, submit=True, delay=10):
        self.submit = submit
        self.delay = delay

    def get_ids(self, ids, sids=False, download_format='sdf',
                compression='gzip', use_3d=False, n_conformers=1):
        """
        Download records for substances or compounds identified by
        PubChem substance IDs (SIDs) or compound IDs (CIDs).

        Parameters
        ----------
        ids : iterable
            PubChem substance or compound IDs.
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
            'structure_format must be one of ' + str(download_formats))
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
        query = query_template % mapping
        rval = PUGQuery(query, submit=self.submit, delay=self.delay)
        return rval


class PUGQuery(object):
    """
    Submit a PUG query and store the download URL when it becomes
    available.

    Parameters
    ----------
    query : str
        PUG query XML.
    submit : bool, optional (default True)
        Whether to automatically submit the query.
    delay : int, optional (default 10)
        Number of seconds to wait between status checks.
    """
    status_template = """
    <PCT-Data>
     <PCT-Data_input>
      <PCT-InputData>
       <PCT-InputData_request>
        <PCT-Request>
         <PCT-Request_reqid>%(id)s</PCT-Request_reqid>
         <PCT-Request_type value="status"/>
        </PCT-Request>
       </PCT-InputData_request>
      </PCT-InputData>
     </PCT-Data_input>
    </PCT-Data>
    """
    url = 'https://pubchem.ncbi.nlm.nih.gov/pug/pug.cgi'

    def __init__(self, query, submit=True, delay=10):
        self.query = query
        self.delay = delay

        self.submitted = False
        self.id = None
        self.download_url = None
        self.filename = None

        if submit:
            self.submit()

    def pug_request(self, query):
        """
        Submit a query to PUG and extract either the query ID or the
        download URL.

        Parameters
        ----------
        query : str
            PUG query XML.
        """
        q = urllib2.urlopen(self.url, query)
        response = q.read()
        print response

        # check for errors
        status_re = re.search('<PCT-Status value="(.*?)"/>', response)
        status = status_re.groups()[0]
        if status not in ['success', 'queued', 'running']:
            raise PUGError('\nQuery:\n------\n{}\n'.format(query) +
                           'Response:\n---------\n{}'.format(response))

        # check for a download URL
        download_url_re = re.search(
            '<PCT-Download-URL_url>\s*(.*?)\s*</PCT-Download-URL_url>',
            response)
        if download_url_re is not None:
            self.download_url = download_url_re.groups()[0]

        # otherwise, extract the request ID
        elif self.id is None:
            reqid_re = re.search(
                '<PCT-Waiting_reqid>\s*(.*?)\s*</PCT-Waiting_reqid>', response)
            self.id = reqid_re.groups()[0]

    def check_status(self):
        """Check the status of the query."""
        assert self.id is not None
        query = self.status_template % {'id': self.id}
        self.pug_request(query)

    def submit(self):
        """Submit the query and monitor its progess."""
        if self.submitted:
            warnings.warn('This request has already been submitted.')
            return
        self.submitted = True
        self.pug_request(self.query)
        while self.download_url is None:
            time.sleep(self.delay)
            self.check_status()

    def fetch(self, filename=None):
        """
        Fetch the result of the query.

        Parameters
        ----------
        filename : str, optional
            Output filename. If not provided, a temporary file is created.
        """
        if not self.submitted:
            self.submit()
        if self.download_url is not None:
            filename, _ = urllib.urlretrieve(self.download_url, filename)
        self.filename = filename
        return filename


class PUGError(Exception):
    """PUG exception class."""
