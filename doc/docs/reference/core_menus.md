# opal.core.menus

Opal provides classes and methods to define application menus programatically.

## opal.core.MenuItem

An item in an application menu.

**Arguments**

* template_name - a template to use to render this menu item
* activepattern - if the current path includes this, add the `active` class
* href - the path to use as the link for this menu item
* icon - an icon name to be used
* display - the text to display in this menu item
* index - a number to use as the primary sort order for your menu items

## opal.core.Menu

The menu for an Opal application. On initialization it will construct a menu
for the current user, pulling items from the current app, and any plugins.
