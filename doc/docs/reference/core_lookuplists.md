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


## {{ LookupListCls }}.objects.search(some_str, case_sensitive=False, contains=False)
A manager method that takes a string and will search accross the lookup list itself or synonyms. If `contains=True` it will look for partial matches. By default it is case
insensitive, to change this behaviour query with `case_sensitive=True`

```python
from opal.core import Antimicrobial

Antimicrobial.objects.search("Difficulty Swallowing")
## returns the Antimicrobial Dysphagia
```

## {{ LookupListCls }}.objects.search_many(list_of_strs, case_sensitive=False, contains=False)
Does the same as the above put takes a list of strings


```python
from opal.core import Antimicrobial

Antimicrobial.objects.search_many(["Fatigue", "Lethargy"])
## returns the Antimicrobial Malaise
```
