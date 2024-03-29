# opal.core.application

### Utility functions

#### get_app

Returns the application class for the currently active application.

#### get_all_components

Returns an iterator of all the of the [plugins](../guides/plugins.md) and the current application

## OpalApplication

The base class for your main application entry point is opal.core.application.OpalApplication.

You must subclass this in order for Opal to discover your application.

If you started your Opal project via `$ opal startproject yourproject` then this will have been
generated for you, and located in `yourproject/yourproject/__init__.py`

### Properties

Properties available on an OpalApplication:

#### OpalApplication.actions

#### OpalApplication.default_episode_category

The default category is 'Inpatient', but can be overridden in the OpalApplication
subclass for your implementation.

#### OpalApplication.angular_module_deps

When you initialise an angular application you need to register dependencies.
This allows you to add to the dependencies of the default opal application.

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

A list of stylesheets that our application would like to include. These should be strings
representing paths ready for staticfiles. Defaults to `[]`. These styles are included after
the default Opal styles.

```python
class MyApplication(OpalApplication):
    styles = ['css/app.css']
```

#### OpalApplication.modify_extract

A list of callables or string paths to functions that will be
called after the files in an extract have been generated but 
before it is zipped and returned to the user.

```python
class MyApplication(Application):
    modify_extract = [
      some_function_to_call_with_extract,
      "string_path_to_function_to_call_with_extract"
    ]
```

The callables are passed:

 * An iterable of episodes in this extract
 * The directory where the zip files for all the subrecords have been stored
 * The user who made the query
 * kwargs reserved for future API alterations

```python
def my_modifier(episodes, path, user, **kwargs):
    if not user.is_superuser:
        return
    count = len(episodes)
    with open(os.path.join(path, 'counter.txt', 'w') as fh:
        fh.write(f"{count} episodes\n")
    return
```



### Classmethods

Classmethod API for OpalApplication instances:

#### OpalApplication.get_core_javascripts(namespace)

Return a list of the core javascript files specified within a given namespace. These will be
relative paths ready for staticfiles.

```python
application.get_core_javascripts('opal.utils')
# -> ['js/opal/utils.js', ...]
```

#### OpalApplication.get_javascripts()

Return a list of the application's javascripts as paths to them ready for staticfiles.
Defaults to returning the `OpalApplication.javascripts` property.

```python
application.get_javascripts()
# -> ['js/one.js', 'js/two.js', ...]
```

#### OpalApplication.directory

Returns the file system location of the module.

#### OpalApplication.get_menu_items(user=None)

Hook to customise the visibility of menu items to e.g. restrict some based on the current
user.

#### OpalApplication.get_styles()

Return a list of the application's stylesheets as paths to them ready for staticfiles.
Defaults to returning the contents of `OpalApplication.styles`.

```python
application.get_styles()
# -> ['css/app.css', ...]
```
