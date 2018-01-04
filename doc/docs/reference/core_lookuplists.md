# opal.core.lookuplists

The `opal.core.lookuplists` module contains utility functions for working with
lookuplists.

## lookuplists()

A generator that will yield every lookuplist currently available to the
application.

```python
from opal.core import lookuplists

for l in lookuplists.lookuplists():
  print l

# -> Drug, Gender, Condition et cetera
```
