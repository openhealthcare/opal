# opal.utils

The `opal.utils` module contains a number of helpful python utilities.

## find_template( template_list )

Given an iterable of template paths, return the first one that
exists on our template path or None.

```python
find_template(['not_a_real_template.html'])
None
```

## write( what )

Writes the argument to `sys.stdout` unless it detects an active test run.
If run during tests, it should do nothing.

Used by Opal for chatty commandline utilities that should be quieter during
test runs.

```python
>>> write('hai')
hai
```
