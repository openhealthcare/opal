## Opal Reference material

The following reference guides are available:

### Models
|
-|-
[opal.models.Episode](episode.md)| The central Episode model
[opal.models.Patient](patient.md) | The Patient model
[opal.models.Subrecord](subrecords.md) | for subrecords of Episodes or Patients
[opal.models.UserProfile](user_profile_model.md) | The Opal UserProfile model
[opal.models.*](mixins.md) | Mixin helpers for useful functionality

### Opal Core
|
-|-
[opal.core.application](opal_application.md) | Opal Application objects|
[opal.core.detail](detail_views.md)|Detail Views - Custom views over one or many episodes.|
[opal.core.episodes](episode_categories.md)|Episode Categories - Controlling the behaviour of different types of episode|
[opal.core.schemas](schemas.md)|Schemas - Dynamic columns for the table views|
[opal.core.patient_lists](patient_list.md)|Patient Lists - defining different types of list|
[opal.core.plugin](plugin.md)| Plugins - defining plugins to package reusable functionality
[opal.core.menus](core_menus.md)| Menus - declaring application menus
[opal.core.log](loggers.md)| Log Helpers - custom email error loggers
[opal.core.fields](core_fields)| Field helpers - custom field types and utility functions|

### Angular Services
|
-|-
[Patient](javascript/patient_service.md) | Patient objects
[Episode](javascript/episode_service.md) | Episode objects
[Item](javascript/item_service.md) |  Subrecord objects
[User](javascript/user_service.md) | User objects
[PatientSummary](javascript/patient_summary_service.md) | Patient search result summaries
[Search Services](javascript/search_js_services.md) | Services from the Search module|
[Loaders](javascript/loaders.md) | JS Services that load in from patient list, episode and patient apis


### Helper libraries

|
-|-
[The forms Templatetag library](form_templatetags.md) | The building blocks for Opal forms
[The panels Templatetag library](panels_templatetags.md) | Rendering record panels
[The menus Templatetag library](menus_templatetags.md) | Rendering application menus
[Javascript Helpers](javascript/javascript_helpers.md)| Angular directives, filters and $rootScope methods

### Opal core modules

|
-|-
[Making Search Queries](search_queries.md) | Search query backends and helper functions
[Pathway](pathways.md)|Simple or complicated multilayed forms|


### Miscellaneous documentation

|
-|-
[Settings](settings.md) | Opal settings
[Changelog](changelog.md) | Opal Changelog
[Upgrading](upgrading.md) | Upgrading between Opal versions
[Javascript dependencies](javascript/javascript_dependencies.md)| External javascript libraries available |
[Testing](testing.md) | Testing
