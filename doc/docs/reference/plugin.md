# Plugins

Opal provides a [plugin mechanism](../guides/plugins.md) to help developers write
generic reusable components.

Plugins must inherit from `opal.core.plugins.OpalPlugin`.

## OpalPlugin

`OpalPlugin` is a [discoverable](../guides/discoverable.md) feature - it will be
automatically discovered by Opal if placed in a `plugin.py` file within an
installed Django app.

## Attributes

- - -

### OpalPlugin.urls

A Django urlpatterns object to add to our urls. Default is [].

- - -

### OpalPlugin.javascripts

A python dictionary containing namespaced sets of javascript files to include in our
application. These will be included on every page by default.

```python
class MyPlugin(OpalPlugin):
    javascripts = {
        'opal.services': [
            'js/myplugin/awesome_service.js'
        ]
    }
```

- - -

#### OpalPlugin.apis

A python iterable of APIs to add to the Django Rest Framework APIs available.

```python
class MyPlugin(OpalPlugin):
    apis = [
        ('ping', api.PingViewSet)
    ]
```

- - -

#### OpalPlugin.stylesheets

A python iterable of stylesheets to add to our application. These will be included on every
page by default.


```python
class MyPlugin(OpalPlugin):
    stylesheets =
        'css/myawesomestyles.css'
    ]
```

- - -

### OpalPlugin.menuitems

A python iterable of items to add to the main menu of our application.

- - -

### OpalPlugin.actions

A Python iterable of templates to include as actions - e.g. additional buttons to add to the
context of a detail, list or other view. These are visible everywhere by default, so care should
be taken to ensire appropriate show/hide logic is present.

- - -

## Classmethods

### OpalPlugin.get_urls()

Returns the Django url patterns to be registered. Defaults to simply returning the `urls`
attribute.

- - -

### OpalPlugin.get_apis()

Returns the APIs to be registered with the Django Rest Framework APIs. Defaults to simply
returning the `apis` attribute.

- - -

### OpalPlugin.directory()

Returns the path to the directory containing the file in which this plugin is defined.
