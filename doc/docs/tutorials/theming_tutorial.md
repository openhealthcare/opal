# Customising the design of your application

Tutorial Outline (WIP)

* Built in settings
* Adding our own CSS file
* Key overrides and a .sass template to reset key colours
* Changing the layout of the application
* Bundling as a standalone theme

## Changing logos

We can change the logo and favicon of our application by changing settings.
Create a logo and a favicon, place them in `./yourapp/static/img/` and then
update the following settings:

```python
# ./yourapp/settings.py

OPAL_FAVICON_PATH = 'img/my.favicon.ico'
OPAL_LOGO_PATH    = 'img/my.logo.png'
```
