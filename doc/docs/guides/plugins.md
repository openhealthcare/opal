# Writing Plugins

OPAL Plugins are Django apps on the server side, and collections of angular.js
models for the client. 

## Getting started with your plugin

Plugins should subclass opal.core.plugins.OpalPlugin

## Defining models

Define in your models.py - just as you would for an implementation.

## Defining Lookup lists

See Defining lookup lists in "Your Implementation.

## Defining teams

As a signal is fine.
Data migrations might work.

Defining restricted team access is done by:

Adding a method to your pluigin that takes one argument, a User object, and returning a set of
extra teams that this user is allowed to see.

## Defining Schemas 

Plugins can define list schemas. They should return a dictionary of lists of models from the
list_schemas() method of the plugin class.

## Defining new flows

Plugins can define flows. They should return a dictionary of flows from the 
flows() method of the plugin class.

## Adding URLS

Add an urls.py, then add to your plugin class as YourPlugin.urls

Naturally, these can point to views in your plugin! 

## Adding Javascript

add to static, then add to your plugin class as YourPlugin.javascripts

There are some restricted namespaces for these...

## Adding dependencies globally to our angular modules

Dependencies listed in `angular_module_deps` will be added to all Angular modules (as long as they
use the OPAL.module() API. If not, you're on your own. We could monkey patch angular.module, but we
won't for now.

## Installing plugins 

Add to installed apps
Add to requirements if appropriate

## Adding extra markup to the <head> tag

Any templates you define in the property .head_extra will be included in the <head>
