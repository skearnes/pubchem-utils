pubchem
=======

Utilities for interacting with PubChem and PubChem BioAssay

Quick Start
-----------

* Download structures for a batch of CIDs

```python
from pubchem import PubChem

cids = [2244, 3672]
filename = 'painkillers.sdf.gz'

p = PubChem()
q = p.get_ids(cids)
q.fetch(filename)
```

* Retrieve SIDs active in a PubChem BioAssay experiment

```python
from pubchem import PubChem

p = PubChem()
sids = p.get_bioassay_ids(466, sids=True, activity_outcome='active')
```
