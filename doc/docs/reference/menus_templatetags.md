# The Menus templatetag library

The `menu` templatetag takes care of rendering an Opal application menu.

It takes one argument - a string of classes to apply to the root menu `<ul>`
element.

```jinja
{% load menus %}
{% menu "nav-right" %}
```
