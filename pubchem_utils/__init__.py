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

    def get_records(self, ids, filename=None, sids=False,
                    download_format='sdf', compression='gzip', use_3d=False,
                    n_conformers=1):
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
            if int(this):  # 0 is not a valid ID
                ids.append(this)
        ids = np.asarray(ids, dtype=int)
        return ids

    def get_assay_data(self, aids, filename=None, substance_view=True,
                       concise=False, compression='gzip'):
        """
        Download PubChem BioAssay data table.

        Parameters
        ----------
        aids : array_like
            PubChem BioAssay IDs (AIDs).
        filename : str, optional
            Output filename. If not provided, a temporary file is created.
        substance_view : bool, optional (default True)
            Whether to group results by substance. If False, results will be
            grouped by compound. The default (True) is recommended when
            retrieving data from a single assay.
        compression : str, optional (default 'gzip')
            Compression type for assay data.
        concise : bool, optional (default False)
            Whether to return the concise data table. If False, the complete
            data table is retrieved.
        """
        query_template = """
<PCT-Data>
  <PCT-Data_input>
    <PCT-InputData>
      <PCT-InputData_query>
        <PCT-Query>
          <PCT-Query_type>
            <PCT-QueryType>
              <PCT-QueryType_bas>
                <PCT-QueryAssayData>
    <PCT-QueryAssayData_output value="csv">4</PCT-QueryAssayData_output>
                  <PCT-QueryAssayData_aids>
                    <PCT-QueryUids>
                      <PCT-QueryUids_ids>
                        <PCT-ID-List>
                          <PCT-ID-List_db>pcassay</PCT-ID-List_db>
                          <PCT-ID-List_uids>
                            %(aids)s
                          </PCT-ID-List_uids>
                        </PCT-ID-List>
                      </PCT-QueryUids_ids>
                    </PCT-QueryUids>
                  </PCT-QueryAssayData_aids>
                    %(dataset)s
                  <PCT-QueryAssayData_focus>
                    <PCT-Assay-FocusOption>
                    %(group_by)s
                    </PCT-Assay-FocusOption>
                  </PCT-QueryAssayData_focus>
                  <PCT-QueryAssayData_compression value="%(compression)s"/>
                </PCT-QueryAssayData>
              </PCT-QueryType_bas>
            </PCT-QueryType>
          </PCT-Query_type>
        </PCT-Query>
      </PCT-InputData_query>
    </PCT-InputData>
  </PCT-Data_input>
</PCT-Data>
"""
        group_by = ('<PCT-Assay-FocusOption_group-results-by value="{}">{}' +
                    '</PCT-Assay-FocusOption_group-results-by>')
        if substance_view:
            group_by = group_by.format('substance', 4)
        else:
            group_by = group_by.format('compound', 0)

        dataset = ('<PCT-QueryAssayData_dataset value="{}">{}' +
                   '</PCT-QueryAssayData_dataset>')
        if concise:
            dataset = dataset.format('concise', 1)
        else:
            dataset = dataset.format('complete', 0)
        aid_xml = ''
        for aid in np.atleast_1d(aids):
            aid_xml += ('<PCT-ID-List_uids_E>{}'.format(aid) +
                        '</PCT-ID-List_uids_E>')
        mapping = {'group_by': group_by, 'dataset': dataset, 'aids': aid_xml,
                   'compression': compression}
        query = PUGQuery(query_template % mapping, submit=self.submit,
                         delay=self.delay)
        rval = query.fetch(filename, compression=compression)
        return rval

    def id_exchange(self, ids, source=None, operation_type='same',
                    output_type='cid'):
        """
        Use the PubChem Identifier exchange service.

        Parameters
        ----------
        ids : iterable
            Input identifiers.
        source : str, optional
            Input source. If None, it will be inferred from ids (if possible).
        operation_type : str, optional (default 'same')
            Operation type. Defaults to exact matches.
        output_type : str, optional (default 'cid')
            Output type. Defaults to PubChem CIDs.
        """
        query_template = """
<PCT-Data>
  <PCT-Data_input>
    <PCT-InputData>
      <PCT-InputData_query>
        <PCT-Query>
          <PCT-Query_type>
            <PCT-QueryType>
              <PCT-QueryType_id-exchange>
                <PCT-QueryIDExchange>
                  <PCT-QueryIDExchange_input>
                    <PCT-QueryUids>
                      <PCT-QueryUids_source-ids>
                        <PCT-RegistryIDs>
        <PCT-RegistryIDs_source-name>%(source)s</PCT-RegistryIDs_source-name>
                          <PCT-RegistryIDs_source-ids>
                            %(source_ids)s
                          </PCT-RegistryIDs_source-ids>
                        </PCT-RegistryIDs>
                      </PCT-QueryUids_source-ids>
                    </PCT-QueryUids>
                  </PCT-QueryIDExchange_input>
                  <PCT-QueryIDExchange_operation-type
                    value="%(operation_type)s"/>
                  <PCT-QueryIDExchange_output-type value="%(output_type)s"/>
                  <PCT-QueryIDExchange_output-method value="file-pair"/>
                  <PCT-QueryIDExchange_compression value="gzip"/>
                </PCT-QueryIDExchange>
              </PCT-QueryType_id-exchange>
            </PCT-QueryType>
          </PCT-Query_type>
        </PCT-Query>
      </PCT-InputData_query>
    </PCT-InputData>
  </PCT-Data_input>
</PCT-Data>
"""
        if np.unique(ids).size != len(ids):
            raise ValueError('Source IDs must be unique.')
        if source is None:
            source = self.guess_source(ids[0])
            if source is None:
                raise RuntimeError('Cannot guess identifier source.')
        mapping = {'source': source, 'operation_type': operation_type,
                   'output_type': output_type}
        source_ids = []
        for source_id in ids:
            id_xml = ('<PCT-RegistryIDs_source-ids_E>' + source_id
                      + '</PCT-RegistryIDs_source-ids_E>\n')
            source_ids.append(id_xml)
        mapping['source_ids'] = ''.join(source_ids)

        # construct query
        query = PUGQuery(query_template % mapping, submit=self.submit,
                         delay=self.delay)
        rval = query.fetch(compression='gzip')

        # identify matched and unmatched IDs
        matched = {}
        for line in rval.splitlines():
            source, dest = line.split()
            if source in matched and matched[source] != dest:
                raise ValueError('Nonidentical duplicate mapping.')
            matched[source] = dest
        unmatched = []
        for source_id in ids:
            if source_id not in matched:
                unmatched.append(source_id)
        return matched, unmatched

    @staticmethod
    def guess_source(identifier):
        """
        Guess the source for an identifier.

        Parameters
        ----------
        identifier : str
            Identifier.
        """
        source = None
        if identifier.startswith('CHEMBL'):
            source = 'ChEMBL'
        elif identifier.startswith('ZINC'):
            source = 'ZINC'
        return source
