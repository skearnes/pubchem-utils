"""
Utilities for interacting with the PubChem Power User Gateway (PUG).

The PUG XML schema is located at
https://pubchem.ncbi.nlm.nih.gov/pug/pug.xsd.

See also https://pubchem.ncbi.nlm.nih.gov/pug/pughelp.html.
"""

__author__ = "Steven Kearnes"
__copyright__ = "Copyright 2014, Stanford University"
__license__ = "3-clause BSD"

import gzip
import re
from StringIO import StringIO
import time
import urllib
import urllib2
import warnings


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
    n_attempts : int, optional (default 3)
        Number of times to attempt query submission.
    verbose : bool, optional (default False)
        Whether to be verbose.
    """
    cancel_template = """
    <PCT-Data>
      <PCT-Data_input>
        <PCT-InputData>
          <PCT-InputData_request>
            <PCT-Request>
              <PCT-Request_reqid>%(id)s</PCT-Request_reqid>
              <PCT-Request_type value="cancel"/>
            </PCT-Request>
          </PCT-InputData_request>
        </PCT-InputData>
      </PCT-Data_input>
    </PCT-Data>
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

    def __init__(self, query, submit=True, delay=10, n_attempts=3,
                 verbose=False):
        self.query = query
        self.delay = delay
        self.n_attemps = n_attempts
        self.verbose = verbose

        self.id = None
        self.download_url = None
        self.filename = None
        self.data = None
        self.alive = False

        if submit:
            self.submit()

    def __del__(self):
        """
        Cancel uncompleted queries.
        """
        warnings.warn('Canceling PUG request.')
        self.cancel()

    def pug_request(self, query):
        """
        Submit a query to PUG and extract either the query ID or the
        download URL.

        Parameters
        ----------
        query : str
            PUG query XML.
        """
        q = None
        for i in xrange(self.n_attemps):
            try:
                q = urllib2.urlopen(self.url, query)
                break
            except urllib2.HTTPError as e:
                if i + 1 < self.n_attemps:
                    continue
                else:
                    raise e
        response = q.read()

        # check for errors
        status_re = re.search('<PCT-Status value="(.*?)"/>', response)
        status = status_re.groups()[0]
        if status not in ['success', 'queued', 'running', 'stopped']:
            raise PUGError(
                '\nQuery:\n------\n{}\n'.format(
                    '\n'.join(query.splitlines()[:100])) +
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

    def cancel(self):
        """
        Cancel a pending request.
        """
        if self.alive:
            query = self.cancel_template % {'id': self.id}
            self.pug_request(query)
            self.alive = False

    def check_status(self):
        """
        Check the status of the query.
        """
        assert self.id is not None
        query = self.status_template % {'id': self.id}
        self.pug_request(query)

    def submit(self):
        """
        Submit the query and monitor its progess.
        """
        if self.alive:
            warnings.warn('This request has already been submitted.')
            return
        self.alive = True
        self.pug_request(self.query)
        if self.verbose:
            print self.id,
        while self.download_url is None:
            if self.verbose:
                print '.',
            time.sleep(self.delay)
            self.check_status()
        if self.verbose:
            print

    def fetch(self, filename=None, compression=None):
        """
        Fetch the result of the query.

        Parameters
        ----------
        filename : str, optional
            Output filename. If not provided, the data is read into memory.
        compression : str, optional
            Compression type used to decode data.
        """
        if not self.alive:
            self.submit()
        if self.download_url is None:
            raise PUGError('No download URL.')

        # fetch
        if filename is not None:
            filename, _ = urllib.urlretrieve(self.download_url, filename)
            self.filename = filename
            return filename
        else:
            data = urllib2.urlopen(self.download_url).read()
            if compression is not None:
                if compression == 'gzip':
                    with gzip.GzipFile(fileobj=StringIO(data)) as f:
                        data = f.read()
                else:
                    raise NotImplementedError(compression)
            self.data = data
            return data


class PUGError(Exception):
    """
    PUG exception class.
    """
