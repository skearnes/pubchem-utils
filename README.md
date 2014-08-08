pubchem-utils [![Build Status](https://travis-ci.org/skearnes/pubchem-utils.svg?branch=master)](https://travis-ci.org/skearnes/pubchem-utils)
=============

Utilities for interacting with [PubChem](https://pubchem.ncbi.nlm.nih.gov)

Quick Start
-----------

Download structures for a batch of CIDs:

```python
from pubchem_utils import PubChem

p = PubChem()
p.get_records([2244, 3672], 'painkillers.sdf.gz')
```

Retrieve SIDs active in a PubChem BioAssay experiment:

```python
from pubchem_utils import PubChem

p = PubChem()
sids = p.get_bioassay_ids(466, sids=True, activity_outcome='active')
```
