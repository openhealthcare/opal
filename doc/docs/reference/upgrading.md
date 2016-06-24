## Upgrading Your OPAL Application

This document provides instructions for specific steps required to upgrading your OPAL
application to a later version where there are extra steps required.

### 6.x -> 7.x

#### Breaking changes

OPAL 0.7 contains a number of breaking changes.

`opal.models.Episode.category` has been re-named `category_name`. If your application
directly sets category, you will be required to update all instances where this happens.

The `/episode/:pk/` API has moved to `/api/v0.1/episode/:pk/` so any code (typically
javascript) code that directly saves to this API endpoint rather than using the OPAL JS
`Episode` services should work immediately when re-pointed at the new URL.

### 4.X -> 5.x

#### Migrations

Before upgrading from 4.x to 5.x you should ensure that you have upgraded from South
to Djangomigrations.

    $ rm yourapp/migrations/*
    $ python manage.py makemigrations yourapp
    $ python manage.py migrate yourapp --fake-initial

#### OPAL

Next you will need to upgrade the OPAL version itself.

How you do this depends on how you have configured your application, but updating your
requirements.txt to update the version should work. This will also update FFS and Django
Axes as well as adding Python Dateutil.

    -e git://github.com/openhealthcare/opal.git@v0.5.6#egg=opal


#### Migrations.

OPAL has fresh migrations in 0.5.x, which we should run. There are also changes to the
base abstract model classes (to add created/updated timestamps) so you'll need to create
fresh migrations for your own application.

    $ python manage.py migrate
    $ python manage.py makemigrations yourapp
    $ python manage.py migrate yourapp

At this stage you'll want to commit your new migrations, as well as any changes to your
application's requirements file.

#### Tags

As of 0.5.5, old tags in OPAL are stored directly on the Tagging model rather than via
Djano Reversion. We can import those old tags by doing the following.

    $ python manage.py shell

    >>> from opal.models import Tagging
    >>> Tagging.import_from_reversion()

#### Deployment

The first time you deploy your upgraded application you'll need to run the following
commands to upgrade your database:

    $ python manage.py migrate --fake-initial

You'll also have to repeat the Tagging step once for each deployment.
