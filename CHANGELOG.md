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

#### Search

Complete re-design of Search interface to provide a single search box on every page and pagination for resulta.
Puts in place a pluggable interface that could be swapped out for e.g. ElasticSearch.
New Service for PatientSummary()

#### Analytics

Moves Analytics integration into OPAL core with the ability to blacklist pages that should never be reported

#### List view

Removed old spreadsheet-style cell based navigation and moved to row-wise nav with clearer highlighting of the active row.
Updated scrolling and loading behaviour to snap to viewport and not display the page build.

#### Subrecord metadata

Added four new utility fields to Patient and Episode subrecords:

created_by, updated_by, created, updated

#### Select2 and list fields

Added support for select2 as an input widget and Subrecord fields that can be lists of things.

#### Also

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

### New Design

Completely re-designed UI following extensive user research and multiple iterations.

### Management commands and scaffolding

Features the opal command line tool for common administrative tasks
http://opal.openhealthcare.org.uk/docs/guides/command_line_tool/

### Form helpers templatetag library

New template library for consistent form controls in line with our new interface guidelines
http://opal.openhealthcare.org.uk/docs/reference/form_templatetags/

### API Documentation


OPAL JSON APIs are now fully self-documenting for all updated instances
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
