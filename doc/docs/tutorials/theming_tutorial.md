# Customising the design of your application

Tutorial WIP

## Changing the default logo and favicon

We can change the logo and favicon of our application by changing settings.
Create a logo and a favicon, place them in `./yourapp/static/img/` and then
update the following settings:

```python
# ./yourapp/settings.py

OPAL_FAVICON_PATH = 'img/yourapp.favicon.ico'
OPAL_LOGO_PATH    = 'img/yourapp.logo.png'
```

Some platforms require favicons to be .ico format, however .png also works

## Adding your own CSS file to change the default colours, fonts, layouts and more

To change the CSS used for the Opal interface, first create a CSS file with your custom application styling:

```css
/* ./yourapp/static/yourapp.css */
body {
  /*main text style*/
  font-family: 'Franklin Gothic Book', Arial;
}

.bg-primary {
  background-color: #25408F; }

.bg-secondary {
  background-color: #0084FF; }
```
Then include this CSS file in your Application definition:

```python
# ./yourapp/__init__.py
class Application(application.OpalApplication):

    styles = [
        "css/yourapp.css"
    ]
```

Many of the classes are standard Bootstrap CSS classes, which can be identified in the Bootstrap documentation, or via the inspector in your browser's developer tools.

## Key overrides and a .sass template to reset key colours

WIP

## Changing the layout of the application

WIP

## Bundling as a standalone theme

WIP

