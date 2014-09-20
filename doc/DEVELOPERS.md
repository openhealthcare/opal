# Your implementation


Your implementation should be a Django project that includes OPAL as a Django app.

## OPAL settings

OPAL_LOG_OUT_DURATION = The number of milliseconds after which to log out our user

OPAL_TAGS_MODULE = DEPRECIATED  TODO: Kill all references to this.

OPAL_BRAND_NAME = The branding to be displayed as the masthead

OPAL_EXTRA_APPLICATION = A template to include in the HEAD

OPAL_EXTRA_HEADER = A template to include above the main nav

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

### _batch_template

Allow the list/detail template access to the complete row, not just an item.
Template is then responsible for registering click handlers.

Will get cix as a variable representing the column index, column_name as the column name.

# Adding a controller

Create the controller file in static/js/opal/controllers.
Use the angular module opal.controllers
Include this file in templates/opal.html
Create a template url in the django layer

# Teams 

Episodes of care are assigned to n teams - broadly a tab in the list view.

Teams have one level of nesting.

Teams may be inactive, in which case they are not displayed.

Teams may be restricted in which they only appear for a subset of users.

The logic for showing restricted teams is implemented via plugins.

# Flow

TBD.

See https://github.com/openhealthcare/opal/issues/214

# Users

Users have various settings:

Can extract
Readonly
Only restricted teams

# Adding a lookup list

Lookup lists are subclasses of opal.utils.models.LookupList which have a generic relation to Synonym and define a foreign key on the calling model.

You can define them yourself, or use the helper function ```opal.utils.models.lookup_list```

    ColourLookupList = type(*lookup_list('colour', module=__name__))

You can then reference the list in a django model by using a ForeignKeyOrFreeTextField 
You can access the list in an angular template (For autocompletion) where it will be $NAME_list.

e.g. The conditions lookup list is condition_list and used by the elCID Diagnosis model
(https://github.com/openhealthcare/elcid/blob/master/elcid/models.py#L109)

As you are creating a new model, you will need a new migration to accompany it. 

If you have initial values for your lookup list, feel free to add them as a data migration. 

The lookup list will automatically be added to the admin.

so e.g. $ python manage.py schemamigration --atuo opal

# Creating a Heroku test server

    $ heroku create $YOUR_APP_NAME

(Edit .git/config to give the remote a meaningful name)

    $ heroku addons:add heroku-postgresql
    $ git push $YOUR_REMOTE_NAME $YOUR_BRANCH:master --app $YOUR_APP_NAME
    $ heroku run python manage.py syncdb --migrate --app $YOUR_APP_NAME
    $ heroku run python manage.py loaddata dumps/options.json --app $YOUR_APP_NAME
    $ heroku run python manage.py createinitialrevisions --app $YOUR_APP_NAME


# Writing Plugins

Plugins are Django apps with some extra hooks.

Plugins should subclass opal.utils.plugins.OpalPlugin

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

## Installing plugins 

Add to installed apps
Add to requirements if appropriate