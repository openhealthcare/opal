# opal.core.application

## OpalApplication

The base class for your main application entrypoints is opal.core.application.OpalApplication.

You must subclass this in order for OPAL to discover your application.

If you started your OPAL project via `$ opal startproject yourproject` then this will have been
generated for you, and located in `yourproject/yourproject/__init__.py`

### Properties

Properties available on an OpalApplication:

#### OpalApplication.actions

#### OpalApplication.default_episode_category

The default category is 'Inpatient', but can be overridden in the
[OpalApplication](opal_application.md) subclass for your implementation.

#### OpalApplication.javascripts

A list of javascripts that our application would like to include. These should be strings
representing paths ready for staticfiles. Defaults to `[]`.

```python
class MyApplication(OpalApplication):
    javascripts = ['js/one.js']
```

#### OpalApplication.menuitems

A list of items to add to the top level menu

#### OpalApplication.styles

### Classmethods

Classmethod API for OpalApplication instances:

#### OpalApplication.get_core_javascripts(namespace)

Return a list of the core javascript files specified within a given namespace. These wil be
relative paths ready for staticfiles.

```python
application.get_core_javascripts('opal.utils')
# -> ['js/opal/utils.js', ...]
```

#### OpalApplication.get_javascripts()

Return a list of the application's javasctipts as paths to them ready for staticfiles.
Defaults to returning the OpalApplication.javascripts property.

```python
application.get_javascripts()
# -> ['js/one.js', 'js/two.js', ...]
```

#### OpalApplication.get_menu_items()
