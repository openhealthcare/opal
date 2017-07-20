# opal.core.fields

The `opal.core.fields` module contains helper functions for working
with fields, as well as custom Opal field definitions.

## is_numeric

A helper function that returns true if a field is numeric. For our
purposes, Integers, Decimals, BigIntegers, Floats and Positive Integers
are considered numeric.

```python
is_numeric(models.IntegerField())
# -> True
```


## enum

A helper function that returns a Django choices definition from star args.

```Python
enum('one', '2', 'III')
# -> (
#     ('one', 'one'),
#     ('2', '2'),
#     ('III', 'III')
#    )
```

## ForeignKeyOrFreeText

A field that stores it's value as a generic foreign key to an Opal LookupList
or as the value in a CharField.
