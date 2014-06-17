Your implemntation
==================

Your implementation should be a Django project that includes OPAL as a Django app.


Defining Models
---------------

Models should be defined in your project.

They should subclass opal.models.EpisodeSubrecord or opal.models.PatientSubrecord as appropriate.

Subrecords have some extra entrypoints that are used by OPAL.

_is_singleton
-------------

_is_singleton is a boolean property that ensures that there is only one of this subrecord per patient/episode.

Effectively this defaults to False.

_title
------

_title sets the column headings in list view.

Effectively this defaults to camel_case_to_underscore() on the class name.

_sort
-----

_sort names a field by which we would like to sorth the display of subrecords.

_fieldnames
-----------

_.fieldnames allows you to specify the list of fieldnames to serialize. This is particularly useful in order to specify ordering within column entry schemas.

Writing Plugins
===============

Plugins should subclass opal.utils.plugins.OpalPlugin