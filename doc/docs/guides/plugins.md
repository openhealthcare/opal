## Writing Plugins

OPAL Plugins are Django apps on the server side, and collections of angular.js
models for the client.

### Getting started with your plugin

The OPAL commandline tool will bootstrap your plugin for you - just run:

    $ opal startplugin yourcoolplugin


### Adding Additional Functionality

Wardrounds, Dashboards and other plugins all add functionality in the same way
and you can too! So the way we do this is very similar to the way django does models
we add a file, for example wardrounds.py This has a bunch of wardrounds that all inherit
from an object. We iterate over objects and get the one that matches our criteria
when we want it, e.g. get me the wardround which has name === "our new wardround". Simple!

To help you create your own, Opal has app_importer.py this contains the get_subclass
which takes in the name of the module to look for the files and the name of the subclass
we want and returns a generator.

For example if you're creating a medicines plugin and you want a view which return medicines
information, for you would create an object that allowed you to configure functionality probably called Medicine that you would expect to be subclassed, then the expectation would
probably be that we would keep all our medicines in medicines.py so we would use
get_subclass("medicines", Medicine) and this would let us iterate over medicines.


### Defining teams

As a signal is fine.
Data migrations might work.

Defining restricted team access is done by:

Adding a method to your pluigin that takes one argument, a User object, and returning a set of
extra teams that this user is allowed to see.

### Defining Schemas

Plugins can define list schemas to be used to generate patient lists.
They should return a dictionary of lists of models from the
`list_schemas` method of the plugin class.

    # yourplugin/__init__.py
    from opal.core.plugins import OpalPlugin

    from yourplugin import models

    class YourPlugin(OpalPlugin):
        def list_schemas(self):
            columns = [models.YourAwesomeModel, models.YourSecondModel, models.SomeOtherModel]
            return {'yourplugin': {'default': columns}}

### Defining new flows

Plugins can define flows. They should return a dictionary of flows from the
flows() method of the plugin class.

### Adding URLS

Add an urls.py, then add to your plugin class as YourPlugin.urls

Naturally, these can point to views in your plugin!

### Adding Javascript

add to static, then add to your plugin class as YourPlugin.javascripts

There are some restricted namespaces for these...

### Adding APIs

OPAL uses Django Rest Framweork to provide APIs, and you may add to these from your plugin.
By convention, APIs live in `yourplugin/api.py`. You are expected to provide a
`rest_framework.viewsets.ViewSet` subclass, which you then detail as the `.apis` attribute
of your plugin.

    # yourplugin/api.py
    from rest_framework.viewsets import ViewSet
    from rest_framework.response import Response

    class PingViewSet(ViewSet):
        def list(self, request): return Response('pong')

    # yourplugin/__init__.py
    from opal.core.plugins import OpalPlugin
    from yourplugin import api

    class YourPlugin(OpalPlugin):
        apis = [
            ('ping', api.PingViewSet)
        ]

These APIs will then be available and self-documenting fom the standard OPAL url `/api/v0.1/`

### Adding Actions to the sidebar

Actions can be added to the sidebar by setting the `actions` attribute of your plugin.
Actions is expected to be an iterable of strings which are templates to be included in
the sidebar. By convention, actions will live in `./templates/actions/` .

    # __init__.py:
    class Plugin(OpalPlugin):
        actions = ('actions/javascript_alert.html', 'actions/dummy_button.html')

And then in the template:

    <p ng-show="episode.category == 'YourEpisodeCategory'">
      <button class="btn btn-primary" ng-click="alert('Boom!')">
        <i href="fa fa-warning"></i>
        ALERT ME
      </button>    
    </p>

### Adding dependencies globally to our angular modules

Dependencies listed in `angular_module_deps` will be added to all Angular modules (as long as they
use the OPAL.module() API. If not, you're on your own. We could monkey patch angular.module, but we
won't for now.

### Installing plugins

Add to installed apps
Add to requirements if appropriate

### Adding extra markup to the <head> tag

Any templates you define in the property .head_extra will be included in the <head>
