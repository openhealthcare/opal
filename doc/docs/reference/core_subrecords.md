# opal.core.subrecords

The `opal.core.subrecords` module contains utility functions for working with
subrecords.

## `episode_subrecords()`

Generator function that iterates through all episode subrecords.

```python
for s in episode_subrecords():
    print(s)

# -> Location, Diagosis et cetera
```

## `patient_subrecords()`

Generator function that iterates through all patient subrecords.

```python
for s in patient_subrecords():
    print(s)

# -> Allergies, ContactDetails et cetera
```

## `subrecords()`

Generator function that iterates through all subrecords.

```python
for s in subrecords():
    print(s)

# -> Allergies, ContactDetails, Location, Diagnosis et cetera
```

## `singletons()`

Generator function that iterates through all singleton subrecords.

```python
for s in singletons():
    print(s)

# -> Location, Demographics
```

## Fetchers

### `get_subrecord_from_api_name(api_name)`

Return a subrecord given the relevant API name for it. Raise a ValueError
if no matching subrecord is found.


```python
get_subrecord_from_api_name('demographics')

# -> <class Demographics>
```


### `get_subrecord_from_model_name(model_name)`

Return a subrecord given the relevant model name for it. Raise a ValueError
if no matching subrecord is found.


```python
get_subrecord_from_api_name('Demographics')

# -> <class Demographics>
```
