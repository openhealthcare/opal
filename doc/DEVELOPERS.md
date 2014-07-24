# Your implementation


Your implementation should be a Django project that includes OPAL as a Django app.

## OPAL settings

OPAL_LOG_OUT_DURATION = The number of milliseconds after which to log out our user

OPAL_TAGS_MODULE = DEPRECIATED  TODO: Kill all references to this.

OPAL_BRAND_NAME = The branding to be displayed as the masthead

OPAL_EXTRA_APPLICATION = A template to include in the HEAD

OPAL_EXTRA_HEADER = A template to include above the main nav


TODO

## Defining Models

Models should be defined in your project.

They should subclass opal.models.EpisodeSubrecord or opal.models.PatientSubrecord as appropriate.

Subrecords have some extra entrypoints that are used by OPAL.

### _is_singleton

_is_singleton is a boolean property that ensures that there is only one of this subrecord per patient/episode.

Effectively this defaults to False.

### _title

_title sets the column headings in list view.

Effectively this defaults to camel_case_to_underscore() on the class name.

### _sort

_sort names a field by which we would like to sorth the display of subrecords.

### _read_only

Marks a field as read only if True

### _fieldnames

_.fieldnames allows you to specify the list of fieldnames to serialize. This is particularly useful in order to specify ordering within column entry schemas.

# Adding a controller

Create the controller file in static/js/opal/controllers.
Use the angular module opal.controllers
Include this file in templates/opal.html
Create a template url in the django layer

# Writing Plugins

Plugins should subclass opal.utils.plugins.OpalPlugin

# Creating a Heroku test server

    $ heroku create $YOUR_APP_NAME

(Edit .git/config to give the remote a meaningful name)

    $ heroku addons:add heroku-postgresql
    $ git push $YOUR_REMOTE_NAME $YOUR_BRANCH:master --app $YOUR_APP_NAME
    $ heroku run python manage.py syncdb --migrate --app $YOUR_APP_NAME
    $ heroku run python manage.py loaddata dumps/options.json --app $YOUR_APP_NAME
    $ heroku run python manage.py createinitialrevisions --app $YOUR_APP_NAME