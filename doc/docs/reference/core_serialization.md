# opal.core.serialization

Helpers for serializing and deserializing data

## `deserialize_datetime(value)`

Given a string which represents a date time, deserialize it to a Python datetime
object using the first value of `settings.DATETIME_INPUT_FORMATS`.

```python
as_datetime = deserialize_datetime('22/04/1959 21:20:22')
```

## `deserialize_time(value)`

Given a string which represents a time, deserialize it to a Python time
object using the first value of `settings.TIME_INPUT_FORMATS`.

```python
as_time = deserialize_time('14:30:59')
```

## `deserialize_date(value)`

Given a string which represents a date, deserialize it to a Python date
object using the first value of `settings.DATE_INPUT_FORMATS`.

```python
as_date = deserialize_date('22/04/1959')
```

## OpalSerializer

A JSON serializer that will serialize the output of `to_dict` calls. This serializer
uses date formats that can be understood by the Opal javascript applications.

```python
import json

as_dict = episode.to_dict(user)
as_json = json.dumps(as_dict, cls=OpalSerializer)
```
