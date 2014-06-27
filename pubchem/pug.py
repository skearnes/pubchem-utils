"""
Utilities for interacting with the PubChem Power User Gateway (PUG).

The PUG XML schema is located at
https://pubchem.ncbi.nlm.nih.gov/pug/pug.xsd.

See also https://pubchem.ncbi.nlm.nih.gov/pug/pughelp.html.
"""

__author__ = "Steven Kearnes"
__copyright__ = "Copyright 2014, Stanford University"
__license__ = "3-clause BSD"

import re
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
