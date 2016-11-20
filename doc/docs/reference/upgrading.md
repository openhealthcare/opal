## Upgrading Your OPAL Application

This document provides instructions for specific steps required to upgrading your OPAL
application to a later version where there are extra steps required.

### 0.7.1 -> 0.8.0

#### Options

Options are now an ex-API. Applications should convert to use either Referencedata (canonical terms for common data), or
Metadata (App specific data you wish to pass into the front end).


#### UI Components

Those applications relying on Angular strap ui components (Typeahead, Popover,
Tooltip, Datepicker, Timepicker) should convert their templates to use the Angular UI Boostrap equivalents, or the
OPAL templatetags. 

If you are simply using Opal templatetags from `forms` and not overriding these templates, then the transition should be seamless. Otherwise, searching your codebase for html files containing `bs-` and looking for angular strap components is a good start.

Applications or plugins with javascript tests may need to update their includes to remove references to old library files.

Full documentation of the markup and options for these components is found [here](http://angular-ui.github.io/bootstrap/versioned-docs/0.14.3/)

#### extending modal_base.html

We now have different base templates for modals, forms and two column modal forms (essentially a form with a side bar).

The form templates add validation checks around the saving to catch any validation errors a form might through. They assume the existence of a form called 'form'.

As part of this modal_base has been moved into a folder in templates called base_templates

Rename any templates extending `modal_base.html` to extend the correct template in `base_templates/` - `modal_base.html` or `modal_form_base.html`.

### 0.7.0 -> 0.7.1

#### Downstream dependencies

OPAL 0.7.1 updates the expected version of Django Axes to 1.7.0 - you will wish to update
this in your requirements.txt or similar accordingly.

#### DRF Authentication

We highly recommend that applications explicitly set Django Rest Framework authentication
classes in their `settings.py`.

By default OPAL now uses session and token auth, which will require a migration to install
the DRF Token authentication app.

```python
INSTALLED_APPS = (
    # ....
    'rest_framework',
    'rest_framework.authtoken',
    # ...
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}
```

### 6.x -> 7.x

#### Upgrading OPAL

How you do this depends on how you have configured your application, but updating your
requirements.txt to update the version should work.

    # requirements.txt
    opal==0.7.0

After re-installing (via for instance `pip install -r requirements.txt`) you will need to
run the migrations for OPAL 0.6.x

    $ python manage.py migrate opal


If you are inheriting from the abstract models in OPAL e.g. `Demographics` then you should
run a makemigrations command to update to the 0.7.x data model.

    python manage.py makemigrations yourapp
    python manage.py migrate yourapp


#### Breaking changes

OPAL 0.7 contains a number of breaking changes.

##### Name changes

`opal.models.Episode.category` has been re-named `category_name`. If your application
directly sets category, you will be required to update all instances where this happens.

The `/episode/:pk/` API has moved to `/api/v0.1/episode/:pk/` so any code (typically
javascript) code that directly saves to this API endpoint rather than using the OPAL JS
`Episode` services should work immediately when re-pointed at the new URL.

##### Moving from options to referencedata and metadata

The signature of the EditItemCtrl has been updated - this modal controller no longer
takes an `options` argument, rather it uses the new 0.7.x `referencedata` and `metadata`
services. Applications that call EditItemCtrl directly should look to update the `resolves`
option they were passing to `$modal.open`. (Alternatively, developers should consider
refactoring to use the new `recordEditor` API.)

The signatures of Flow `enter` and `exit` methods has changed to no longer accept
options as a positional argument, and enter/exit controllers will no longer be initialized
with access to options as a resovled provider. They will have access to either/both of
`referencedata` and `metadata` so if your application includes custom flow controllers that
use `options` you will need to refactor these to use the new x-data arguments instead.

`referencedata` and `metadata` between them have all data previously in options, so the refactor
here should be relatively painless.

##### Date of birth fields in forms

The partial `partials/_date_of_birth_field.html` has been removed and replaced with the
`{% date_of_birth_field %}` templatetag in the forms library. You should update any forms
to use this new tag.

### 5.x -> 6.x

#### Upgrading OPAL

How you do this depends on how you have configured your application, but updating your
requirements.txt to update the version should work.

    # requirements.txt
    opal==0.6.0

After re-installing (via for instance `pip install -r requirements.txt`) you will need to
run the migrations for OPAL 0.6.x

    $ python manage.py migrate opal

#### Changes to abstract models

If you are inheriting from the abstract models in OPAL e.g. `Demographics` then you should
run a makemigrations command to update to the 0.6.x data model.

    python manage.py makemigrations yourapp
    python manage.py migrate yourapp

You should note that as of OPAL 0.6.x `Demographics` now splits names into first, surname,
middle name and title. The previous `name` field will be converted to be `first_name`.

Strategies for updating your data to use the appropriate fields will vary from application
to application, but one good such strategy is to use a data migration [such as the one done
here](https://github.com/openhealthcare/acute/blob/master/acute/migrations/0004_auto_20160624_1215.py).

#### Update settings

Many of the default OPAL templates now assume that the `'opal.context_processors.models'`
Context Processor is available - you should add that to the `TEMPLATE_CONTEXT_PROCESSORS`
setting in your application's `settings.py`

The default date formats in OPAL have changed - and so you should update your `DATE_X`
settings to match:

```python
DATE_FORMAT = 'd/m/Y'
DATE_INPUT_FORMATS = ['%d/%m/%Y']
DATETIME_FORMAT = 'd/m/Y H:i:s'
DATETIME_INPUT_FORMATS = ['%d/%m/%Y %H:%M:%S']
```

#### Upgrade plugins

A number of OPAL plugins have new releases to work with the changes in OPAL 0.6.x

* opal-referral - Upgrade to 0.1.4
* opal-wardround - Upgrade to 0.6.0
* opal-observations - Upgrade to 0.1.2
* opal-dischargesummary - Upgrade to 0.2.0
* opal-dashboard - Upgrade to 0.1.3

Meanwhile the `opal-taskrunner` plugin has now been deprecated, this functionality now
living natively within OPAL core.

#### Update your Teams to be PatientLists

Patient Lists are now driven by subclasses of `opal.core.PatientList`, so we will need
to convert your Teams to be PatientLists. You may want to re-enable the Team admin while
you do so - this is simple, by updating your application's `admin.py`:

    # yourapp/admin.py
    ...
    from opal.admin import TeamAdmin
    from opal.models import Team
    admin.site.register(Team, TeamAdmin)


Patient lists are now declarative. For instance, to replicate the following team:

<img src="/img/resp.team.png" style="margin: 12px auto; border: 1px solid black;"/>


We would convert that to:

```python
# yourapp/patient*lists.py
from opal.core import patient_lists

class RespiratoryList(patient_lists.TaggedPatientList):
    display_name = 'Respiratory'
    tag          = 'respiratory'
    order        = 4
    schema       = [models.Demographics, models.Treatment]
```

The schema property will likely be available to you in your application's `schema.py`
file - which is now obsolete.

See the [full patient list documentation](../guides/list_views.md) for further details
of the options available for Patient Lists.

#### Form and Display templates.

We may now be missing some form or display templates, as your application may be
relying on templates previously in OPAL. To discover which these are, run

    $ opal scaffold --dry-run

You may either create templates by hand, or have OPAL generate boilerplate templates for you
by running `$ opal scaffold`.

Modal templates already in your application will likely be referencing invalid paths
to their Angular variables. You should update these to include the record name - for example:

```html
<!-- Was -->
{% input  label="Drug" model="editing.drug" lookuplist="antimicrobial_list" %}
<!-- Becomes -->
{% input  label="Drug" model="editing.treatment.drug" lookuplist="antimicrobial_list" %}
```

#### The Inpatient episode category

The default Episode Category - Inpatient episodes has updated it's database identifier
from `inpatient` to `Inpatient`. To update your episodes run :

```python
>>> from opal.models import Episode
>>> for e in Episode.objects.filter(category='inpatient'):
...   e.category='Inpatient'
...   e.save()
...
```

Any references to episode category in templates (for e.g. ng-hide) or controllers for logic
will also require updates.

#### Flow is now defined in JS

Flow is no longer defined on the server side in python, but rather is a javascript service.
See the documentation for information about setting up custom flows. At a minimum applications
that use custom flows will have to implement their own flow service and reference it in their
settings.

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
