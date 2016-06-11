# opal.core.application

## OpalApplication

The base class for your main application entrypoints is opal.core.application.OpalApplication.

You must subclass this in order for OPAL to discover your application.

If you started your OPAL project via `$ opal startproject yourproject` then this will have been
generated for you, and located in `yourproject/yourproject/__init__.py`

### Properties

#### OpalApplication.actions

#### OpalApplication.default_episode_category

The default category is 'Inpatient', but can be overridden in the
[OpalApplication](opal_application.md) subclass for your implementation.

#### OpalApplication.javascripts

#### OpalApplication.menuitems

A list of items to add to the top level menu

#### OpalApplication.styles

### Classmethods

#### OpalApplication.get_core_javascripts(namespace)

Return a list of the core javascript files specified within a given namespace.

    application.get_core_javascripts('opal.utils')
    # -> ['js/opal/utils.js', ...]

#### OpalApplication.get_menu_items()
