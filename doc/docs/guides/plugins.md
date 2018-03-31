## Writing Plugins

Opal Plugins are Django apps on the server side, and collections of angular.js
models for the client.

### Getting started with your plugin

The Opal commandline tool will bootstrap your plugin for you - just run:

```bash
$ opal startplugin yourcoolplugin
```

### Adding Discoverable Functionality

A common pattern for plugins is to add functionality that other plugins or applications
can use by inheriting a base class that you define in a file with a magic name. (In
much the same way that Django provides models.)

For example, if you're creating an appointments plugin that helps people to book and schedule
appointments in clinics, you would create a base `Clinic` class that can be subclassed to
create specific clinics.

```python
class Clinic(opal.core.discoverable.DiscoverableFeature):
    module_name = 'clinics'
```

We can then create clinics in any installed app, and they will be available from `Clinic.list()`

```python
class OutpatientsClinic(Clinic):
    name = 'Outpatients'

    # Add your custom clinic functionality here e.g.
    def book_appointment(self, date, patient):
        pass


Clinic.list()
# -> Generator including OutPatientsClinic

Clinic.get('outpatients)
# -> OutpatientsClinic
```

### Getting a plugin directory

Each plugin has a `directory()` method that returns the file system location of the module.

### Adding URLS

Add an urls.py, then add to your plugin class as YourPlugin.urls

Naturally, these can point to views in your plugin!

### Adding Javascript

Add to static, then add to your plugin class as YourPlugin.javascripts

There are some restricted namespaces for these...

### Adding APIs

Opal uses Django Rest Framework to provide APIs, and you may add to these from your plugin.
By convention, APIs live in `yourplugin/api.py`. You are expected to provide a
`rest_framework.viewsets.ViewSet` subclass, which you then detail as the `.apis` attribute
of your plugin.

```python
# yourplugin/api.py
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

class PingViewSet(ViewSet):
    def list(self, request): return Response('pong')

# yourplugin/plugin.py
from opal.core.plugins import OpalPlugin
from yourplugin import api

class YourPlugin(OpalPlugin):
    apis = [
        ('ping', api.PingViewSet)
    ]
```

These APIs will then be available and self-documenting from the standard Opal url `/api/v0.1/`

### Permissioning

Developers are strongly encouraged to ensure that APIs which
serve patient data are restricted to logged in users. Django Rest Framework `ViewSet` classes
have an [extensive permissioning system](http://www.django-rest-framework.org/api-guide/permissions/).

Opal ships with the base ViewSet class `opal.core.api.LoginRequiredViewset` which adds the Django
Rest Framework permission class IsAuthenticated to your viewset.


```python
class PingViewSet(LoginRequiredViewset):
    def list(self, request):
        return Response('pong')
```

### Adding Actions to the sidebar

Actions can be added to the sidebar by setting the `actions` attribute of your plugin.
Actions is expected to be an iterable of strings which are templates to be included in
the sidebar. By convention, actions will live in `./templates/actions/` .

```python
# plugin.py:
class Plugin(OpalPlugin):
    actions = ('actions/javascript_alert.html', 'actions/dummy_button.html')
```

And then in the template:

```html
<p ng-show="episode.category == 'YourEpisodeCategory'">
  <button class="btn btn-primary" ng-click="alert('Boom!')">
    <i href="fa fa-warning"></i>
    ALERT ME
  </button>
</p>
```

### Adding dependencies globally to our angular modules

Dependencies listed in `angular_module_deps` will be added to all Angular modules (as long as they
use the OPAL.module() API. If not, you're on your own. We could monkey patch angular.module, but we
won't for now.

### Adding Menu items

Plugins may add items to the main Opal Menu by setting the `menuitems` attribute.
This attribute should be an iterable of [`MenuItem`](../reference/core_menus.md) objects.

```python
from opal.core import menus

class YourPlugin(OpalPlugin):
    menuitems = [
        menus.MenuItem(href="/your-url", icon="fa-user")
    ]
```

### Installing plugins

* Add the plugin's name to the `INSTALLED_APPS` list in your `settings.py`

* Add the plugin's name to `requirements.txt` and run `pip install -r requirements.txt` (if appropriate, eg if you are distributing your plugin via Pypi or GitHub) 

### Adding extra markup to the <head> tag

Any templates you define in the property .head_extra will be included in the <head>
