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

By default this is case insensitive, pass in `case_sensitive=True` to make
it case sensitive when matching against lookup lists or synonyms.

e.g.
```python
class Duck(object):
  name = ForeignKeyOrFreeText(Name)
  show = ForiegnKeyOrFreeText(Show, case_sensitive=True)

Name.objects.create(name="Scrooge")
Show.objects.create(name="Duck Tales")

scrooge = Duck()

# by default we are case insensitive, so this will be saved
# as a foreign key to a Name object
scrooge.name = "scrooge"
# ie now
scrooge.name == "Scrooge"
scrooge.name_fk == Name.objects.get(name="Scrooge")


# this is not a case sensitive field so will be stored on the model as free
# text
scrooge.show = "duck tales"

# ie
scrooge.show_ft == "duck tales"

```
