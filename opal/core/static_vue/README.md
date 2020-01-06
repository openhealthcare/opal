This package allows an opal user to easily use vue in your project.

Add `django-webpack-loader==0.6.0` to your requirements.txt
Add `whitenoise==5.0.1` to your requirements.txt
Add `frontend/node_modules/*` to your .gitignore

Add `opal.core.static_vue` and `webpack_loader` to your `INSTALLED_APPS`

Also add to `settings.py` (Not we're changing the `STATICFILES_DIRS`)
```
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
STATICFILES_DIRS = [
    os.path.join(FRONTEND_DIR, 'dist'),
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MIDDLEWARE.insert(0, "whitenoise.middleware.WhiteNoiseMiddleware")

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': DEBUG,
        'BUNDLE_DIR_NAME': '/bundles/',  # must end with slash
        'STATS_FILE': os.path.join(FRONTEND_DIR, 'webpack-stats.json'),
    }
}
```


Your base template should have something that looks like...

```
{% load render_bundle from webpack_loader %}

<html>
    <head>
        {% render_bundle "app" "css" %}
    </head>
    <body>
    <div id="app">
    </div>
    {% render_bundle 'app' "js" %}
    <script>
      {% block vue_instance %}
      new Vue({
        el: '#app',
      })
      {% endblock %}
    </script>
    </body>
</html>
```


then run the management command `setup_static`



In the new front end directory run...

`npm run serve` to watch the static assets.
`npm run build` to buil the static assets.
`npm run lint` to line the static assets.
`npm run jest` to test the static assets.

If you don't need to change the static assets. We're loading in a precompile version.
If you do, you can but run `npm run serve` locally and `npm run build` before you push.

TODO.

1. deploy a test run to heroku, _should_ just work.
2. `static_asset_paths` as is does not work. It's been tested on a branch but only in and hoc manner... Let's make sure.
3. Unit tests.
4. If we're happy, update the scaffold so this comes as default.
5. Update the default opal app to produce a `.scss` which imports opal.
6. Change the opal colour schema variables to sass defaults so they can be updated by the application.
(This allows applications to easily do colour schemes out of the box)
7. Change components to be imported by default as per the vue docs.







