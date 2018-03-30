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

## get( object, attribute, default=None )

Similar to the `getattr` builtin, `get` will fetch an attribute of on object.

If there is a `get_` method defined, `get` will use that in preference to
direct object accesss.

If there is no `get_` method defined and DEFAULT is passed, use
that as the default option for `getattr()`.

```python
class PoliteConversation(object):

    formal_greeting = 'Hello'

    @classmethod
    def get_greeting(klass):
        return 'Hi'


get(PoliteConversation, 'formal_greeting')
"Hello"

get(PoliteConversation, 'greeting')
"Hi"
```
