pubchem-utils [![Build Status](https://travis-ci.org/skearnes/pubchem-utils.svg?branch=master)](https://travis-ci.org/skearnes/pubchem-utils)
=============

Utilities for interacting with [PubChem](https://pubchem.ncbi.nlm.nih.gov)

Quick Start
-----------

```python
from pubchem_utils import PubChem
p = PubChem()
```

Download 3D structures for a batch of CIDs:

```python
p.get_records([2244, 3672], filename='painkillers.sdf.gz', use_3d=True)
```

Retrieve SIDs active in a PubChem BioAssay experiment:

```python
sids = p.get_ids_from_assay(466, sids=True, activity_outcome='active')
```

Download the data table for a PubChem BioAssay experiment:

```python
p.get_assay_data(466, filename='AID466.csv.gz')
```

Get the PubChem CID for a compound in [ChEMBL](https://www.ebi.ac.uk/chembl):

```python
id_map = p.id_exchange('CHEMBL25')  # source is inferred from ID string
```

Search PubChem for the CID matching a SMILES string:

```python
cid = p.structure_search('CC(=O)OC1=CC=CC=C1C(=O)O')
```
