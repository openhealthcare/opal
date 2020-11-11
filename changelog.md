### 0.20.0 (Major Release)

#### Updates to the Dependency Graph

* Django: 2.0.13 -> 2.2.16


### 0.18.4 (Minor Release)

#### Some models have translations
Episodes/Patients/Demographics now use use gettext_lazy on all their fields

#### PatientListCtrl.refresh and PatientDetailCtrl.refresh return promises
PatientListCtrl.refresh and PatientDetailCtrl.refresh now return a promise which resolves after the refresh is complete.

#### Removes scroll to top
Removes the directory `scrolllto-top` as this is not commonly used. `go-to-top` is directive that is a a drop in replacement that will take the user up to the top of the page but without scrolling.

#### Remove shortDate and shortDateTime
The angular filters shortDate and shortDateTime have been deprecated for some time.

#### Stop an index being passed to recordEditor.editItem
recordEditor.editItem used to take either a number or an item (subrecord) as its second argument.
Now it will only take an item.

#### Removes the account page
Removes the user account detail page as this is not tested/used and can be easily created within an app.

### 0.18.3 (Minor Release)

#### Complex objects are now serialized in the extract as json
If you have a dictionary, or a list of dictionaries returned by Subrecord.to_dict, these will now be serialized into
the dictionary as json, rather than str(dict)

### 0.18.2 (Minor Release)

#### inpatient.html is now in the scaffold
Previously `inpatient.html` (the template for the default episode category) was in opal. Now it is put directly into new apps with `opal startproject`.

`inpatient.html` also has had a banner stating the episode category removed.

Bug fix for the date field template so that it can be a required field (either through the template or inferred from the db field).

### 0.18.1 (Minor Release)
Bug fix removing js files from the core app that have now been removed.

### 0.18.0 (Major Release)

#### Load lookuplist data format

Fixes a bug (1695) to ensure that the data keys inside a lookuplist data file are taken
from the value of `.get_api_name()`.

#### Allow extract queries for 'falsy' values

Fixes a bug in extract. When querying against 0 or false the ui stated that no query had been entered. Also queries on multiple fields that included a filter against a field with 0 or false would have that portion of the query ignored.

#### Ment.io and Macro removal

The Macro feature and related Ment.io library have been removed. (No known applications used these features.)

#### Remove additional EpisodeCategories

The Outpatient and Liaison episode categories have been removed from `opal.core.episodes`. Defining
these here rather than expecting applications to define them in application land means that overriding
templates can only be done via monkeypatching.

#### FindPatientStep removal

Removes the `FindPatientStep`. Every known application with this functionality has required custom logic
and re-written this step. (If there is a common case, we don't know what it is yet.)

#### Profile can_see_pid removal

The `can_see_pid` method of profiles on both the front and back end was tied to hard-coded roles which
were impossible to override.

#### Micro test removals

A large number of microbiology specific models and lookuplists have been removed from this version of
Opal along with the Investigation model. This code was rarely used and turned out to be incompatible
wiht subsequent LIMS system integration. We would advise anyone using it to incorporate these models
into their own applications, but consider moving away.

#### Line Lookuplist removals

Removes line removal reason, complication, site and type lookuplists. These are rarely if used and
would be better placed at present in an application rather than the core framework.

#### Javascript API removals

Removes the undocumented `EditItemCtrl.prepopulate` method. Custom Pathway controllers are recommended
for complex form interactions.

Also removes a series of Angular filters which were deemed of limited re-use potential. Applications may
add such filters themselves trivially.

* microresult
* boxed
* plural

Removes the undocumented `UserProfile.can_edit` method. This made assumptions about specific named roles
which were unconfigurable and was thus unlikely to be useful.

#### Flow based controllers removed

Removes the HospitalNumberCtrl and AddEpisodeCtrl along with related tests and templates. Pathways
can perform thse operations significantly more flexibly.

This has also resulted in removing the undocumented Episode method `findByHospitalNumber` which was
used by the flow controllers.

#### Allergies sidebar

Removed an undocumented template `modals/_allergies_sidebar.html` which was rarely used and more suited
to being included in individual applications than the framework itself.

#### Stories

The Stories functionality is not clearly more useful than simply having an html template file in an
individual application. The pattern of having them as individual feature files which are not executalbe
by e.g. Cucumber adds complexity but no value. Explicit acceptance tests are encouraged for applications,
but no longer live as part of Opal core.

#### Design Patterns

Removes the design patterns library as this is incompatible with the new 'skinability' approach. Such
patterns pages are encouraged for large applications or standalone themes.

#### Plugin/Application stylesheet media atribute

Style sheets loaded via Opal Applicatin or Plugin objects are now included with the attribute `media="all"`
rather than `media="screen".

#### Minor Bugfixes

* For some types, e.g. decimal the core serilizer would return `None`. This is now resolved.
* Deletes a directory previously left as an artifact of scaffolding at ../../js/app/ (1554)

#### Updates to the Dependency Graph

* DjangoRESTFramework 3.7.4 -> 3.10.2
* python-dateutil 2.7.5 -> 2.8.0


### 0.17.1 (Minor Release)
Removes a now deleted file from the default application javascripts list

### 0.17.0 (Major Release)

#### Javascript API removals

Removes the function Episode.isDischarged() (This was rarely if ever used,
and no longer an accurate represenation of dischargedness.)

Removes the Episode.getNumberOfItems method which is rarely used.

Removes the methods PatientDetailCtrl.dischargeEpisode() and PatientListCtrl.dischargeEpisode()
(However you're discharging episodes as of 0.17 it would be strongly unadvisable to do it this way.)

Removes PatientList.removeFromMine()
(The special casing of the 'Mine' list is strongly unadvised and set for complete removal.)

Removes the front end Flow service


#### Miscelanious changes

Bumps Flake8 version to 3.7.8 - new code will now be required to pass flake8 v3.7.8

#### Updates to the Dependency Graph

* Jinja2: 2.10 -> 2.10.1
* Psycopg2: 2.7.6.1 -> 2.8.3
* Requests: 2.20.1 -> 2.22.0

#### python3
Opal now only supports python 3.5 - python 3.7

### 0.16.0 (Major Release)

Adds serialize_date, serialize_datetime, serialize_time utility functions to serialize date/datetime/time to
strings.

Diagnosis.details is now a text field.

Changes the requirements.txt files that get created when we create an opal application or plugin to use `python-dateutil==2.7.5`

### 0.15.0 (Major Release)

Adds an optional setting OPAL_DEFAULT_SEARCH_FIELDS that specifies the fields used to
search in when a criteria isn't specified.

### 0.14.2 (Minor Release)

Documentation fix, we're on python 3.4 now.

### 0.14.1 (Minor Release)

The search plugin was not excluding search strings from analytics.
This change makes it so that it does.

### 0.14.0 (Major Release)

A User's UserProfile is now automatically created when you create a user in a post save signal.

RecordEditor.editItem, RecordEditor.editItem and RecordEditor.openEditItemModal to take a url argument.
This is the url of the template that should be opened with the edit item controller.

RecordEditor.editItem also will now take an item or an index rather than just an index.
Taking an index has been deprecated and will be removed in v0.15.0

The PatientListCtrl now does the logic of whether to create a new item or edit an item within the
controller before it calls the record editor.

### 0.13.1 (Minor Release)

Upgrades the setup.py Django version from 2.0.9 to 2.0.13. Removes the six library dependency from setup.py.

### 0.13.0 (Major Release)

#### Removes support for Python 2.x

Due to the upgrade to Django 2.x, Opal no longer supports Python 2.x.

Opal is now tested against Python 3.5, 3.6

#### Episode.active

The field `Episode.active` was previously implicitly set when calling `.set_tag_names()` to
something equivalent to the value of `bool(len(tag_names) > 0)`.

As of 0.13.0 the value of `Episode.active` is checked whenever `.save()` is called, prior
to the database call. The correct value is looked up via `Episode.category.is_active()`.

The default calculation of `.active` has also changed to be roughly equivalent to
` bool(self.episode.end is None)`.

Applications are now able to easily _change_ this behaviour by overriding the `.is_active`
method of the relevant `EpisodeCategory`.

#### Coding systems for lookuplists

Lookuplist entries may now have an associated coding system and code value stored against them.

This enables applications to explicitly code entries against e.g. SNOMED value sets.

Note: This will requires a migration to be created for all applications.

#### New date display format helpers

Introduces two new Angular filters: `displayDate` and `displayDateTime`. These format a date
for display according to the setting `DATE_DISPLAY_FORMAT`. This defaults to `D MMM YYYY`.

New applications will have this setting in their scaffold, existing applications may wish to add
it.

All core Opal templates that previously used `shortDate` or `shortDateTime` have been updated to
use either `displayDate` or `displayDateTime`.

#### Removes scope.jumpToEpisode and scope.getEpisodeId from Search and Extract

We no longer use these functions, instead we use an HTML link to the patient detail view.

#### Removes Patient.to_dict().active_episode_id

We no longer include a value for "active_episode_id" as part of the Patient to_dict serialisation.

This is effectively meaningless since we moved to an episode model that allows for multiple
concurrent episodes.

#### Removes CopyToCategory

Removes the entire CopyToCategory flow from Opal Core. If applications continue to rely on it,
they are advised to implement at application level.

In general application developers are advised to find alternative ways to display subrecords
from multiple episodes rather than copying them however, as this is known to cause duplication
of data that is hard to trace back later on.

This includes the API endpoint at `episode/$id/actions/copyto/$category/`, the template
`copy_to_category.html`, the Angular controller `CopyToCategoryCtrl` and service
`CopyToCategory` and Subrecord property `_clonable`.

#### Lookuplist data format

Lookuplist entries in data files are no longer required to have an empty synonyms list
if the entry doesn't have a synonym. This reduces the file size and makes it easier to
hand craft data files for new applications.

#### TaggedPatientList Episode serialisation

Alters the default serialisation of TaggedPatientList serialisation to no longer filter out
'inactive' episodes. Given that 'active' was always true when an episode had a tag, this
was effectivly a no-op anyway unless applications were altering the `get_queryset` for
these patient lists somehow.

#### Removes the deprecated Model._title property

Use of `Model._title` to set a display name of a subrecord has issued a warning for several
releases - this has now been removed and will no longer work.


#### Free text or foreign key fields are now, by default case insensitive

This can be adjusted with a flag on the field.

Existing fk_or_ft fields could therefore still have the field set as free text.

This change is not accompanied by a retrospective migration so your existing fk_or_ft may be
stored in a case sensitive manner. It is recommended you migrate all of your fk_or_ft fields
as this will give you consistent behaviour.

##### For example

Prior to this change if I had an allergy for "paracetomol" but an entry in the models.Drug
table of "Paracetomol", it would be stored as free text in the `Allergies.drug` field, because
it was case sensitive. Going forward after this change it will be saved as a foreign key. This
change will not be made retrospecively however so you would need to add a migration that resaved
the Allergies.drug.

#### Misc Changes

* The undocumented Reopen Episode flow included in Opal < 0.8.0 has now been completely removed,
including the `reopen_episode_modal.html` template and the url/view at `templates/modals/reopen_episode.html/`.

* Removes the method `.deleteItem` from the `RecordEditor` service.

* Adds in a footer updated/created by to the form base template

* Changes the default value of `_ft` fields on `ForeignKeyOrFreeTextField` from b'' to ''. This requires a migration

* `__unicode__` model methods have been renamed `__str__`

* Adds an index argument to `PatientList.as_menuitem()` and `Pathway.as_menuitem()`

* Adds a `get_absolute_url()` method to `Patient` and `Episode

* Adds `btn-cancel`, `btn-save` and `btn-delete` classes to the respective form buttons.

* Moves the cancel button by default to be left of the save button.

* Renames the (undocumented, internal) Angular service `FieldTranslater` to `FieldTranslator`

* If an item is deleted from the edit item modal, RecordEditor.openEditItemModal will now resolve after
  the delete item modal is closed with 'deleted'

#### Updates to the Dependency Graph

* Django: 1.10.8 -> 2.0.9
* Django Rest Framework: 3.4.7 -> 3.7.4
* Django Reversion: 1.10.2 -> 3.0.1
* Letter: 0.4.1 -> 0.5
* Requests: 2.18.4 -> 2.20.1
* Psycopg2: 2.7 -> 2.7.6.1
* Python Dateutil: 2.4.2 -> 2.7.5


### 0.12.1 (Minor Release)
* If an item is deleted from the edit item modal, RecordEditor.openEditItemModal will now resolve after the delete item modal is closed with 'deleted'

* Fixes the default investigation modal


### 0.12.0 (Major Release)

#### Misc Changes
* Adds the {% block analytics %} in the base template (opal/templates/base.html) that by default contains the google analytics code.

* Adds the block {% block javascripts %} in the base template (opal/templates/base.html) that will compress all javascripts.

* Adds a method `.demographics()` to `opal.models.Patient` which returns the relevant demographics instance.

* Adds a `for_user` method on to the menu item. This method
takes a user and by default returns True. Override this
to decide if a menu item should be shown in the nav bar.

### 0.11.2 (Bugfix Release)

Includes referencedata JSON files in Manifest.

### 0.11.1 (Bugfix Release)
Fixes the user_options in the date picker tag to display the options as part of the text input.

### 0.11.0 (Major Release)

#### Adds options of `today` and `yesterday` in the date picker

If you pass in `user_options=True` to the date picker. You will be provided with
options to select today or yesterday in the form tag.

#### Adds `dateHelper` to the rootScope

The dateHelper has the functions `now` and `yesterday` that return javascript Dates for
the current time and the current time - 1 day.

#### Deprecates the _title property

In future we will use the standard `verbose_name` property as the display name.
The abstract models have been changed to account for this.

#### Core API registration

A refactor in the way that the core APIs are registered by Opal means that
importing `opal.core.api` in a plugin API no longer results in circular imports.

Fixes a bug whereby episodes were serialising differently depending on whether
the code path went via `.to_dict()` or `.objects.serialised()`.

#### HelpTextStep can now use a custom template

The `opal.core.pathway.steps.HelpTextStep` can now have a `help_text_template` passed in.

This is the template for what will be placed in the side bar.

#### Adds in a radio_vertical template tag

This displays the label and then the radio
buttons as a vertical list.

#### opal.core.serialization

A number of helpers related to serialization and deserialization have been brought
together in the new module `opal.core.serialization`.

#### Removes "episode_history" from episode serialization

Serialised episodes previously contained a "shallow" copy of all other episodes in
a property named `episode_history`. This was primarially useful before we switched
from episode-oriented to patient-oriented detail views by default.

This also includes a change to the signature of the `.serialised()` method of the
Episode manager, which no longer accepts a `episode_history` kwarg.

#### as_menuitem helpers

Applications using Opal Menuitems often wish to add menu items for Patient Lists and
Pathways.

To aid this, the `.as_menuitem()` method now creates one from the target class with
sensible but overridable defaults.

#### `opal serve` command

We add `opal serve` to the Opal commandline tool. Currently this simply wraps the
Django runserver management command. It is envisaged that in the future this will
also initialize e.g. sass precompilers with a single command.

#### Misc Changes

Adds the utility function `opal.utils.get`. Similar to the `getattr` builtin, `get` looks
for a method named `get_$attr` and will call that if it exists.

Adds the method `.get_absolute_url()` to `opal.core.pathways.Pathway` and
`opal.core.patient_lists.PatientList`.

#### Template removals

We removed a number of superfluous templates:

* opal/templates/patient_lists/spreadsheet_list.html
* opal/templates/layouts/left-panel.html

#### Static asset minification

The Django upgrade in Opal 0.10 stopped compressor minifying files
when DEBUG is set to False. This fixes that issue by upgrading Django compressor to
a version that supports Django 1.10.

#### The return of an old friend: IE Document modes

Users report that their system administrators sometimes configure Internet Explorer
in such a way that it uses e.g. IE7 Document mode by default.

This is problematical for Opal applications which do in fact make use of internet
technologies that were in widespread use after say, 2006.

We have altered `base.html` to specify `"X-UA-Compatible" content="IE=Edge"`. If you
override `base.html`in your application we advise that you add this `<meta>` tag.

#### Misc Changes

* Adds the utility function `opal.core.subrecords.singletons()` which returns
a generator function which will yield all subrecord singletons.
* Fixes a URI encoding bug in the `Episode.findByHospitalNumber()` method that
made hospital numbers including `#` or `/` raise an error.
* Adds the methods `.get_absolute_url()`, `.get_icon()` and `get_display_name()`
to `opal.core.pathways.Pathway` and `opal.core.patient_lists.PatientList`.

#### Updates to the Dependency Graph

* Django compressor: 1.5 -> 2.2


### 0.10.1 (Minor Release)

#### Plugin API end points can now override application end points

A change to the order that APIs are registered with Django Rest Framework allows
plugins to now override the core Opal application APIs.

#### Fonts are now locally sourced

Fonts are now served from Opal's static assets rather than from the Google CDN.

#### print/screen stylesheets have been collapsed into opal.css

Print/screen differences are now in opal.css with media tags.

#### Google Analytics is now deferred

The loading in of Google Analytics is now deferred to the bottom of the body
tag to allow the page to load without waiting on analytics scripts to load.

#### Scaffold version control failures

The `startplugin` and `startproject` commands initialize a git repository by
default. If we (The `subprocess` module) cannot find the `git` command, we now
continue with a message printed to screen rather than raising an exception.

#### Episode.objects.serialised now uses select_related

`ForeignKeyOrFreeText` fields now have their ForeignKey items preselected when
we use `Episode.objects.serialised`. This provides a speed boost for applications
with moderately heavy `ForeignKeyOrFreeText` usage.

(Approx 30-40% in our tests.)


### 0.10.0 (Major Release)

This is a major release with breaking changes from upstream dependencies.
You are almost certain to require changes to your application. Please see
the upgrade guide for further details.

#### Referencedata in new applications

Opal now includes core lookuplist data in an `opal.core.referencedata` plugin
which is installed and loaded by default by the `startproject` scaffolding.

#### Deletion cascade behaviour

Opal 0.10 changes several behaviours related to cascading deletions which, despite
being Django defaults, were confusing to users and developers in our use case.

When we delete and look up list instance, we no longer delete all subrecords that use
that instance. Instead we set the look up list instances name in the free text field on
the subrecord.

When you delete a user, it will no longer delete all related episodes and subrecords

#### Episode Category stages

Episode categories now enforce a set of valid `Episode.stage` values.
`EpisodeCategory` now includes the `.get_stages()` and `.has_stage(stage)` methods,
while `Episode` has a `set_stage` setter which is used by the UpdateFromDictMixin JSON API.

#### lookuplists.lookuplists

Adds the utility generator `lookuplists.lookuplists()` which wil yield every lookuplist
currently available.

#### Discoverable.filter()

Disoverable features now have a `filter` method which allows you to filter features
with matching attributes.

#### Pathways ContextProcessor

The 'opal.core.pathways.context_processors.pathways' Context Processor will allow you to
access your pathways from templates without having to explicitly load them in a view. In
turn, this allows patterns like:

    {% include pathways.YourPathway.get_display_name %}


#### Missing consistency token errors

`.update_from_dict()` will now raise the new error
`opal.core.errors.MissingConsistencyTokenError` if it is called without a consistency
token when one is set on the model. Previously it would raise `APIError`.

The JSON API will now return a more specific message in the response boday, explaining
that the problem is a missing consistency token.

#### dump_lookup_lists --many-files

Adds the `--many-files` option to the `dump_lookup_lists` command which will write
each installed lookup list to a separate file in the `./data/lookuplists` directory
of the application.

#### Template removals

We remove a number of stale unused templates:

* changelog.html
* contact.html
* extract_footer.html
* tagging_detail.html
* _helpers/inline_form.html
* responsive/_phone_episode_list.html'
* responsive/_tablet_episode_list.html

#### Removing LoginRequiredMixin

As Django ships with a `LoginRequiredMixin` of its own we no longer roll our own
in `opal.core.views.

#### Testing options

Adds a `--failfast` option to the test harness to stop test runs on the first
failure.

If you are a plugin developer upgrading an existing plugin you will have to
manually add support for `--failfast` passthrough to your `runtests.py`.

If you are a plugin developer upgrading an existing plugin you will have to
manually add support for `--failfast` passthrough to your `runtests.py`.

#### Moves scaffold to be a django management command

The rest of the api is still the same but now
we run `python manage.py scaffold {my_app_name}`

#### Deprecations completed

As previously noted in console warnings, the Angular Episode service no longer
supports the `discharge_date`, `date_of_admission`, `date_of_episode` properties.
These were replaced by `.start` and `.end`.

#### Updates to the Dependency Graph

* Django: 1.8.13 -> 1.10.8
* Django Reversion: 1.8.7 -> 1.10.2
* Django Rest Framework: 3.2.2 -> 3.4.7
* Psycopg2: 2.5 -> 2.7
* Jinja2: 2.9.6 -> 2.10
* Ffs: 0.0.8.1 -> 0.0.8.2
* Requests: 2.7.0 -> 2.18.4
* django-celery: 3.1.17 -> 3.2.2
* celery: 3.1.19 -> 3.1.25

#### Misc Changes

Removes the undocumented `collapsed_multisave` tag from the `pathways` templatetag
library.

Adds a setting `OPAL_FAVICON_PATH` to specify the application Favicon to use.

Adds the `rows` option to the textarea template tag which just fills in the html textarea
`rows` attribute. Text areas are defaulted to 5 rows (the same as before).

Configures the setting `CSRF_FAILURE_VIEW` to use the bundled `opal.views.csrf_failure` view.

Pathway slugs may now include hyphens as well as numbers, lower case letters and underscores.

Bugfix: in edit_item.js $scope.episode_category is now set from episode.category_name
as opposed to episode.category (which was always null)

Fixes some instances of progressbars not being reset if unexpected error states
occur.

Improves the rendering of patient detail pages where no patient with the ID from
route params exits. (Displays a polite message instead of erroring.)

Incorrect pluralisation of subrecord names in the Admin view has been fixed. (Migrations
will have to be run in all models which extend the changed core Opal models (this is due
to a minor upstream Django bug)

Minor change to the diagnosis form.

### 0.9.0 (Major Release)

#### Good bye date_of_episode, discharge_date, date_of_admission

And hello `episode.start` and `episode.end`. These fields on the `Episode` model
replace the multiple ways of recording Episode duration in Opal.

There is a migration that sets `start` to date_of_episode if it  exists, otherwise
it uses date of admission.

`end` will be date_of_episode if it exists, otherwise it will use discharge_date.

Note that this means we no longer refer to start and end properties on the
Episode category. If you override `start` and `end` in a custom episode category
you should update to use the Episode model fields. This logic should be moved into
your flows and you'll need to put in a migration to populate existing
episodes.

We also remove the episode fields `date_of_episode` `discharge_date`, and
`date_of_admission`.
Warning: Backwards migrations will not migrate back to `date_of_episode` but to
a admission and discharge. Take backups before running these migrations!

The fields `start` and `end` are both cast to moments (rather than raw js Dates) on
episode.initialisation

#### Pathway

Moves the opal-pathway module into the opal core. Pathways is an extensible way
of creating forms that involve multiple subrecords.

#### We've got time on our side

Adds in the {% timepicker %} template tag, that follows the same convention as
the other template tags, ie {% timepicker field="Dinner.time" %}

#### Removes a js global declaration of categories

Previously we declared CATEGORIES globally. This has now been removed

#### Order Order

Episodes in the patient list are now ordered by start, first_name and surname

#### Theming support

Improvements and better documentation and guides for theming applications. Particularly
of note are changes to `opal.html` and `base.html`, as well as the addition of the
`static_page.html` template.

This version also includes extensive improved support for customising the templates that
display patient lists, detail views, menus and forms amongst other things.

For full documentation, consult the theming guide in the documentation.

#### Makes search fully pluggable

Search is now completely pluggable, you need to have *some* angular controller
called SearchCtrl, but apart from that you can plugin your own implementation.

#### Exclude prefixes now work on actual paths

Previously they only worked with angular paths, now they work
with a combination of actual paths and angular url paths (e.g. /search/#/extract)

#### Misc Changes

Add the allow_add_patient and allow_edit_teams options to the patient lists.

We added support for a `--file` or `-f` option for the `load_lookup_lists` command which
allows the user to specify a particular file outside of the default locations.

The default `Location` record display template will no longer include references
to `Episode.start`. and `Episode.stop` labelled as admisssion and discharge to support
the majority case where an episode relates to something other than an inpatient episode!

Applications wishing to retaint this functionality should update their own temaplates
to display start/stop details.

#### Removes Deprecated functionality in ReferenceData, Metadata, UserProfile and recordLoader

Previously these would make their http request when imported into a file. They now require you to call .load()
for them to return the promise that loads in their respective data.

### 0.8.3 (Minor Release)

#### opal.log.ConfidentialEmailer
Adds a custom email logger. This enables Django error emails which remove any confidential patient data.

Also adds in the karma config to the MANIFEST.in so that we include the karma configs on pip install. It also moves it
to "opal/tests/js_config/karma_defaults.js".

### 0.8.2 (Minor Release)

#### OPAL_LOCATION is added as a system variable when running js tests
If you run opal test js, your karma config is now run in an environment that has
access to the OPAL_LOCATION variable which points to the opal parent directory.

#### A Data Dictionary In The Extract
The Extract zip file has a data dictionary with human readable metadata about each field.

#### Enhanced Application menus

The application menu API, previously python dicts stored in attributes on either plugin or
application subclasses, now consists of the new `opal.core.menus.MenuItem` class, enabling
enhanced customisation and flexibility.

#### PUT to the episode API returns the episode with all its subrecords
Previously it only returned the episode. Now it matches the episode create api end point

#### Episode/Patient links in admin
In the admin, episodes and patients lists now have links to the patient detail pages.

#### User data for the client

Adds a `User` Angular service that enables applications to use user data.
Also adds some directives to make it easy to render User names and avatars.

#### Episode.getFullName()

Adds a utility method to the `Episode` service that returns a human readable patient name.

#### Plugin.get_javascripts, Plugin.get_styles

Enhances the API available for plugins to include javascript and css by adding methods on
`opal.core.plugins.OpalPlugin`

#### 'element_type' argument for the form template tags

Numeric database fields are now set as the html5 type="number" when rendering
them with the forms templatetag library. This means on mobile devices it will
bring up the numeric keypad. The element type can now be set via the template
tag API with the 'element_type' argument.

#### OPAL_LOGO_PATH

This new setting allows applications to set the path at which the app logo is served.
If `OPAL_LOGO_PATH` is set, the value is passed to the `{% static %}` templatetag to set
the `src` atribute of an image in the default application header and login screen.

#### Inactive episodes in PatientLists

Changes the behaviour of `opal.core.PatientList.to_dict` to serialise inactive
episodes by default rather than filtering by Episode.active == True.

`opal.core.TaggedPatientList.to_dict` continues to filter by Episode.active ==
True by default.

#### Notice of future removals

The context variables `brand_name` `settings` and `extra_application` in `opal.views.IndexView`
are no longer helpful thanks to the settings context processor. These will be removed in
0.9.0 and emit warnings until then.

#### Misc changes

Adds a new filter - `underscore-to-spaces` for removing underscores from strings.

The options for `SymptomComplex.duration` have moved from the default form template to a choices
declaration on the model. These are scheduled to move again to a lookuplist.

The default value of `Subrecord.get_display_name` now uses Django `Meta.verbose_name`.

#### Minor fixes

Fixes a bug where the allergies form rendered the provisional field twice

#### Updates to the Dependency Graph

Upgrades Font Awesome from 4.3.0 -> 4.7.0
Upgrades Jinja2 from 2.8 -> 2.9.6

### 0.8.1 (Minor Release)

#### Cookies for the future

We now use the `$cookies` api as part of moving to angular v1.5.8.

The default expiry of cookies is now a year in the future.

The cookie name previously stored as `opal.lastPatientList` is now
`opal.previousPatientList`.

#### Patients as a service

Patient becomes a service in angular. This takes in a patient as loaded by the patient loader or another service. It casts the data to Episode or Item instances as appropriate.

#### PatientList.get_queryset arguments

PatientList.get_queryset() is now passed an extra keyword argument - `user`.
This is the current `User` object.

#### Overriding default Menu Items behaviour

The `get_menu_items` method of Opal Application objects is now passed an extra keyword argument - `user`.
This is the current `User` object.

The templatetag application_menuitems now uses this method to render navigation menus, allowing dynamic
customisation of menu contents based on user.

#### Removals

Opal 0.8.1 removes some minor features which, to our knowledge are not used by any applications in active development.

* ReopenEpisodeCtrl - applications may implement their own 're-open' episode flow, but Opal no longer handles this out of the box.
* Subrecord._bulk_serialise - this flag has been removed

#### Pending removals

We have re-named `opal.core.views._build_json_response` to `opal.core.views.json_response`. This will issue a
warning for the remainder of the 0.8.x branch, before being removed entirely in Opal 0.9.0.

#### Subrecord List API

We have added a list method to the default Opal JSON API for subrecords - you may now obtain a list of all instances
of a given subrecord from the API endpoint `/api/v0.1/$api_name/`.

#### Misc Changes

Updates the custom `UserAdmin` so that the email, first and last name fields from the Django `User` model
are in the add user form not just the edit user form.

The default test runner generated by plugin scaffolding now uses `opal.urls` as the default url conf in the test settings. This allows you to test urls generated by Opal - for instance default form or record templates, or simply raw templates from our generic template view.

### 0.8.0 (Major Release)

#### Plugins

Plugins have been refactored and are now `DiscoverableFeatures`. This should have no impact on existing
plugins, however the functions `opal.core.plugins.register` and `opal.core.plugins.plugins` are slated for
removal in 0.9.0

When creating new plugins we will place the plugin definition class in `plugin.py` rather than `__init__.py`

#### opal.core.api.patient_from_pk

A decorator that changes a method that is passed a pk, to a method that is passed a patient.


#### ToDictMixin._bulk_serialise

Adds a flag to the to dict mixin to determine whether the item is serialised as part of `Episode/Patient.to_dict`.


#### Fixes bugs in add many subrecord radio buttons

Previously multiple radio buttons for the same subrecord field on the same page would
not appear to the user to update correctly. This has now been fixed.


#### Angular UI Libraries

0.8.0 consolidates Angular UI libraries bundled with Opal. We have removed Angular Strap, and
switched all components using it to their Angular UI Bootstrap equivalents.

This is a breaking change.

Applications taking advantage of the `Forms` templatetag library should require no updates, but will see
some minor differences in visual style of widgets.

Detailed upgrade guides for the components affected (Typeahead, Popover,
Tooltip, Datepicker, Timepicker) are available in the upgrade reference documentation.

#### Defaults for Client Side subrecords

We pull through default values from subrecord fields into the Opal `Schema` and use those values when initializing the relevant
Item instance for a new subrecord. This should greatly reduce the need to use custom Angular subrecord services to set defaults.

#### Choices in form templatetags

Template tags that use the 'field' attribute to point to a subrecord field will now infer a lookup list from the Choices of the field if it exists.

Note unlike the traditional choices implementation only the last value of the choices is used and saved to the database

```python
  Colours = (
    ('P', 'Purple'),
    ('R', 'Red'),
  )
```

What is displayed to the user and saved to the database is 'Purple' or 'Red' respectively.

#### element name in template tags

The html attribute 'name' for form elements generated with the Opal `{% forms %}` templatetag library used to be inferred from the model name. Although this remains the default you can also set it with an angular expression:

```html
{% select field="Demographics.first_name" element_name="...Your Angular expression..." %}
```

#### Model removals

The models `Team`, `GP`, `CommunityNurse` and `LocatedModel` - marked for removal since 0.6.0
have now been removed.

As part of this change, the add episode modal previously available at
`/templates/modals/add_episode.html/` is now not available at the url with a trailing slash.
Any controllers attempting to open the modal e.g. custom list flows should update their
`$modal.open` call to remove the trailing slash.


#### Python 3

Opal 0.8.0 is the first version of Opal to support Python 3. This has meant changing the default
ordering of `PatientList` instances to 0 rather than None.

Moving forwards we expect all new code in Opal to be compatible both Python 2.7 / 3.4 / 3.5 / 3.6.

This introduces an explicit Opal dependency on the Six module for maintaining codebases that span
Python 2.x and 3.x.

#### Tabbed Patient List Groups

Adds the class `opal.core.patient_lists.TabbedPatientListGroup` which displays groups of related
lists as tabs at the top of each member list.

#### PatientList sort order

To enable custom sort orders for individual `PatientList`s we introduce the `comparator_service` attribute.
This names an Angular service which will return a list of comparator functions.

#### PatientList Arbitrary columns

We now explicitly enable columns in spreadhseet lists that are not tied to subrecords. These can be
included in PatientList schema instances as explicit Column() entries.

#### Template re-naming

Modal_base has now been moved into a folder called base_templates. Its also now got a form_modal_base and a two_column_form_modal_base.
The latter two templates add validation around saving.

The standard edit item models and others now inherit from the form_modal_base.

#### Authorization and permissions

All APIs should be permissioned with Django REST framework permission classes. The default implementation uses
opal.core.api.LoginRequiredViewset, a standard DRF viewset that requires the user to be logged in.

We now require the user to be logged in for any use of the search functionality.

Added a custom interceptor that logs the user out if the we receive a 403 or 401 from the server

#### Form Validation

Adds the checkForm directive

e.g.

```html
<button check-form="form" ng-click="sendDataToTheServer">click me</button>
```

This adds default form submission behaviour to the a button. It will check if the form is valid, and if its not it will mark the button as disabled until it becomes valid.

It will also set the form as submitted.

We also now show the required error if the form has been submitted or if the field is dirty, so that the user doesn't get an ugly "fill this field in now" message when opening the modal/pathway but will get the error after they click submit.

#### Removals

Opal 0.8.0 removes a number of un-used features that have been slated for removal for some time:

* `Options` - both from the JSON API, and the Angular service.
* The legacy APIs `/api/v0.1/episode/admit` and `/api/v0.1/episode/refer`.
* The models `GP`, `CommunityNurse` and `LocatedModel`.
* `opal.models.Tagging.import_from_reversion`. This one-off classmethod on tagging was introduced to aid with the upgrade from Opal 4.x to 5.0 and has no further utility.
* The `static` argument from the forms `input` tag. Developers should move to the `static` tag.
* The _modal option to set on subrecords. This is because we now use large modals across the board.


#### Misc changes

The opal.core.api.EpisodeViewSet.create now expects tagging to be an object rather than a list, similar to how it details with demographics and location.

The API will no longer serialise the _ft or _fk_id fields of FreeTextOrForeignKey fields - these
are internal implementation details of the server that are not useful on the client side.

Adds a Unique Together constraint for (Tagging.user, Tagging.episode, Tagging.value)

Look up lists now load in from individual apps. The look for a file at {{ app }}/data/lookuplists.json

The default admin url is now `/admin/` - rather than `/admin/?` this results in more readable
admin urls and is closer to what most applications do with the Django admin.

The roles field `opal.models.UserProfile.roles` has been updated to be `blank=True`. This allows the editing
of users without specific roles assigned in the Django admin. Although this introduces no changes at the
database level, this does introduce a migration.

#### Updates to the Dependency Graph

Upgrades angular to v1.5.8 (from 1.3.11) you can see their change log [here](https://github.com/angular/angular.js/blob/master/CHANGELOG.md)

Updates angular-cookies and angular-mocks to v1.5.8 (both from 1.3.11)

Updates angular-ui-select to 0.19.4 from 0.13.2

### 0.7.5 (Minor Release)

The flow enter and exif functions now take an optional context argument. When called from PatientList or PatientDetail controllers this is the parent scope when the flow has been entered.

Note: The current Flow API is likely to undergo substantial revision in Opal 0.9 / 0.10 do contact us on the mailing list if you are relying heavily upon it or would like to let us know your needs.

### 0.7.4 (Minor Release)

Adds  a past filter, future and past filters now take a
boolean argument as to whether you should include today

### 0.7.3 (Minor Release)

Fixes a bug whereby celery tasks are not autodiscovered - will have affected users of async extract functionality.

### 0.7.2 (Minor Release)

Fixes a bug with the copy to category API not setting category name.

Removes the hangover use of options in the list of teams per episode in the patient list

### 0.7.1 (Minor Release)

Completes the refactor of front end data, no longer using the `/api/v0.1/options/` API internally.
This is slated for removal in 0.8.0.

Updates DRF APIs - we now expect either Token or DjangoSession auth.

Fixes several small bugs with scaffolded applications -  the setting of `STATIC_ROOT` and
`SECRET_KEY`, generating forms for NullBooleanFields, requirements.txt.

Adds an `aligned_pair` templatetag to the `panels` library.

Updates the label for `Demographics.birth_place` to indicate that this should be a country.

Adds the `clipboard` directive to give the user one click copy to clipboard.

Adds a `tag-select` directive that renders a widget for editing the tags for an episode.

Adds metadata to the scope for patient detail views

#### Updates to the Dependency Graph

* Django Axes 1.4.0 -> 1.7.0

### 0.7.0 (Major Release)

#### Episode Categories

Refactors EpisodeCategory to be a discoverable feature.

Renames `Episode.category` -> `Episode.category_name`.

#### Episode JSON API

The Restful Episode JSON API previously available at `/episode/:pk/` is now moved into
`/api/v0.1/episode/:pk/` for consistency with the rest of our JSON APIs.
The Opal Angular layer has been updated to reflect this, and
should handle the transition seamlessly, but code calling the API directly should update
to reflect the new URL.

#### Defaults for records on the client side

Establishes a new way to define defaults for records initialized in Javascript without
requiring that we hard-code API names to defaults in a global namespace.


#### Update to Javascript Signatures

`Flow.enter()` and `Flow.exit()` now no longer take `options` positional arguments - instead
the controllers they initialize have `Metadata` and `Referencedata` as optional resolves
arguments.

AddEpisodeCtrl now no longer requires options as a resolves() option, but requires Referencedata
instead.

#### MaxLength for form helpers

The `input` form helper will now infer the max length of char fields from the max length of the
database field, and render relevant Angular directives.

#### EpisodeDetail removed

The `EpisodeDetailCtrl` and `EpisodeDetailMixin` controller and service have been removed - these
were not used anywhere other than in the Wardround plugin, and redundant after enhancements to
Patient Detail and Custom DetailViews in 0.6.

#### Additional utilities

Adds a datetimepicker templatetag that will render widgets for a Datetime field including time.

Adds a `date_of_birth_field` templatetag that renders a date of birth field complete with inteligent
validation. (Note this change also includes removing the old _partial/ template)

Updates dependency graph:

* Django -> 1.8.13

### 0.6.0 (Major Release)


**Detail views**

Moves from episode oriented detail to patient oriented detail.
(All episodes plus x-episode views are available from a patient detail screen)

**Tagging**

As a performance optimisation for the frequent access of historic tags, untagging
an episode simply renders the tag inactive rather than deleting it and relying on
Django-Reversion for access to historical data.

**Date Formatting**

We now expect 'd/m/y' date formatting by default.

**Patient lists**

Lists are now declarative, and separate from teams. They are implemented as
subclasses of opal.core.patient_lists.PatientList.

**Forms vs. Modals**

Introduces a distinction between a form and a modal.
By default, we now use forms for subrecords, only overriding the modal if there
is something we want to do differently specifically in the modal.

**Command line tools**

Adds $opal checkout for switching between applications or application versions.

### Models ContextProcessor

The 'opal.context_processors.models' Context Processor will allow you to access your
subrecords from templates without having to explicitly load them in a view. In turn,
this allows patterns like:

    {% include models.Demographics.get_detail_template %}


#### Upgrade instructions:

Full upgrade instructions to work through any backwards incompatible changes are
provided in the Opal docs.

### 0.5.5 (Minor Release)
Changes the way old tags are handled.

Tags are no longer deleted episodes, rather they're marked as archived.


### 0.5.4 (Minor Release)
* Include local storage


### 0.5.3 (Minor Release)
* Speed up loading of the lookup lists
* Fix pagination issues in search
* Speed up loading of many to many fields
* Increase test coverage
* Add some extra help fields to {% forms %} helpers
* Fixes bug with $rootScope.open_modal() where keystrokes were being intercepted

### 0.5.2 (Minor Release)
Speed improvements on page load
allow us to only show record panels if a record of that type exists
disable modal buttons while saving


### 0.5.1 (Minor Release)
Minor bug fixes


### 0.5 (Major release)

**Search**

Complete re-design of Search interface to provide a single search box on every page and pagination for resulta.
Puts in place a pluggable interface that could be swapped out for e.g. ElasticSearch.
New Service for PatientSummary()

**Analytics**

Moves Analytics integration into Opal core with the ability to blacklist pages that should never be reported

**List view**

Removed old spreadsheet-style cell based navigation and moved to row-wise nav with clearer highlighting of the active row.
Updated scrolling and loading behaviour to snap to viewport and not display the page build.

**Subrecord metadata**

Added four new utility fields to Patient and Episode subrecords:

created_by, updated_by, created, updated

**Select2 and list fields**

Added support for select2 as an input widget and Subrecord fields that can be lists of things.

**Also**

Numerous small bugfixes.
Refactoring of the models package into a models module.
Updated Underscore.js -> 1.8.3
Updated Angular.js -> 1.3.11

### 0.4.3 (Minor release)

Refactors opal.models to be a models.py file rather than a package.
Adds several improvements to forms helpers -> Help argument, other argument to select.

Updates dependency graph:

* Angular-strap -> 2.3.1

### 0.4.2 (Minor release)

Upgrades dependency graph:

* Django -> 1.8.3
* Django-reversion -> 1.8.7
* jQuery -> 1.11.3
* D3 -> 3.5.6
* C4 -> 0.4.10

South has been removed, now using django migrations

### 0.4.1 (Bugfix release)

Fixes some search results appearing duplicated.

### 0.4 (Major release)

**New Design**

Completely re-designed UI following extensive user research and multiple iterations.

**Managementcommands and scaffolding**

Features the opal command line tool for common administrative tasks
http://opal.openhealthcare.org.uk/docs/guides/command_line_tool/

** Form helpers templatetag library**

New template library for consistent form controls in line with our new interface guidelines
http://opal.openhealthcare.org.uk/docs/reference/form_templatetags/

**API Documentation**


Opal JSON APIs are now fully self-documenting for all updated instances
http://opal.openhealthcare.org.uk/docs/guides/json_api/

### 0.3 (Major release)

Bugfixes, significant flexibility in template customisability.

Minor UI updates.

### 0.2.2 (Bugfix release)

Numerous small bugfixes.

Adds the concept of undischarging patients.

### 0.2.1

Numerous small bugfixes.


### 0.2.0

Search overhaul - introduces advanced searches.

### 0.1.1

Initial public release
