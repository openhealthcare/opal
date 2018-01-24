# opal.core.discoverable

The `opal.core.discoverable` module contans base discoverable classes for creating
features which can be re-used and subcalssd.

## DiscoverableFeature

The base discoverable class which provides functionality to all discoverables.

**DiscoverableFeature properties**

### DiscoverableFeature.module_name

The name of the python module in which Opal will look for instances of this
discoverable. For instance in the following feature, Opal would look in every
installed app at `app/ciao.py` for subclasses of `Greeting`, even if that module
had not been directly imported already.

```python
from opal.core import discoverable

class Greeting(discoverable.DiscoverableFeature):
  module_name = 'ciao'
```

### DiscoverableFeature.display_name

The human readable name for an instance of a discoverable. Use this in the UI
when showing the discoverable to users.

### DiscoverableFeature.slug

The slug for this discoverable used in URLs. Note that Opal internally useses
the `get_slug` method below to allow more dynamic slugs.

** DiscoverableFeature classmethods **

### DiscoverableFeature.is_valid()

Stub function that is called at class definition to determine whether an instance
is valid. Useful for enforcing business logic and expectations for third party
features. Expected to raise an exception if something is wrong.

### DiscoverableFeature.get_slug()

Return the slug for this feature. Defaults to returning the `slug` property if
it is set, or running a slugify function on the `display_name`. If neither is
set it will raise a ValueError.

```python
MyFeature.get_slug()
# -> "my-feature"
```

### DiscoverableFeature.list()

Return a generator that yields all implementations of a discoverable.

```
for g in Greeting.list():
    print g.display_name

"Bonjour"
"Hola"
"Namaste"
"Salaam"
```

### DiscoverableFeature.filter(**kwargs)

Find instances of a feature based on the value of their attributes. You may pass
attributes of features as keyword arguments. Returns a list of matching features.

```python
Greeting.filter(module_name='ciao') # Essentially the same as .list()

Greeting.filter(slug="bonjour", display_name="Bonjour")
# -> [BonjourGreeting]
```

## SortableFeature

A mixin class that provides ordering for features which will be respected
by both `list()` and `filter()`.

** Properties **

### SortableFeature.order

An integer which is used to sort features.

** SortableFeature classmethods **

### SortableFeature.list()

Returns instances of the feature orderd by `.order`

```python
class Greeting(discoverable.DiscoverableFeature,
               discoverable.SortableFeature):
    module_name='ciao'

class Namaste(Greeting):
    order = 2

class Hello(Greeting):
    order = 32098239021

class Bonjour(Greeting):
    order = 1

for f in Greeting.list():
    print f, f.order

# <class '*.*.Bonjour'>, 1
# <class '*.*.Namaste'>, 2
# <class '*.*.Hello'>, 3

```

## RestrictableFeature

A mixin class that provides an interface for restricting access to features based on
user.

```python
class Greeting(discoverable.DiscoverableFeature,
               discoverable.RestrictableFeature):
    module_name='ciao'

```
** RestrictableFeature classmethods **

## RestrictableFeature.for_user(user)

Generator method that yields all instances of this discoverable which are visible to
a given user.

```
for f in Greeting.for_user(user):
    print f

# <class '*.*.Bonjour'>
# <class '*.*.Namaste'>
# <class '*.*.Hello'>
```

## RestrictableFeature.visible_to(user)

Predicate function used to determine whehter in individual feature should be visible
to a given user. Defaults to simply returning True.

Features may override this to provide restricted access as required.

```python
Hello.visible_to(user) # -> True
```
