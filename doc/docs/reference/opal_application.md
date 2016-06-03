# opal.core.application

##OpalApplication

The base class for your main application entrypoints is opal.core.application.OpalApplication.

You must subclass this in order for OPAL to discover your application.

If you started your OPAL project via `$ opal startproject yourproject` then this will have been
generated for you, and located in `yourproject/yourproject/__init__.py`

### schema_module

### javascripts

### actions

### menuitems

A list of items to add to the top level menu

### default_episode_category

The default category is either 'inpatient', but can be overridden in the [OpalApplication](opal_application.md) subclass for your implementation.
