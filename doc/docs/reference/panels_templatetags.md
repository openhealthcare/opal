# Panel helpers

Opal comes with a selection of templatetags for rendering Opal panels
for a given subrecord. These panels also allow the user to
see instances of the model against the current value of `episode` in
Angular `$scope`. The user can also create new
instances of the given model, as well as editing any existing ones.

### {% record_panel ... %}

Render a panel for a given record that will allow the user to view, create, update and delete instances.

The record panel template expects the relevant Angular `$scope` to have `newNamedItem(name, index)`,
`editNamedItem(name, index)` and `deleteItem(name, index)` methods implemented. Default
implementations of these are available from the `EpisodeDetailMixin`.

    {% load panels %}
    {% record_panel Diagnosis %}

Keywords:

* `model`: The model we want to render our panel for
* `title`: The display title for this panel
* `detail_template`: The display template to use. Defaults to Subrecord.get_detail_template()
* `editable`: Whether this panel should allow editing. Defaults to True.
* `angular_filter`: An Angular expression that will be evaluated to decide whether to show each item
* `noentries`: A string to render if there are no instances of `model` for the current episode
* `only_display_if_exists`: Boolean defaulting to False. If true, the panel will simply not render if there are no instances of `model`

### {% record_timeline ... %}

Similar to `record_panel`, `record_timeline` renders a panel for a given record as a timeline - particularly
useful for subrecord types where the date is a key field.

    {% load panels %}
    {% record_panel Diagnosis 'when' %}


Arguments:

* `model`: The model we want to render our panel for
* `whenfield`: String of the field that we're using to sort by.

### {% aligned_pair ... %}

Render a key value pair in their own Bootstrap row using columns of width `md-4` each.
Particularly useful for occasions when we have multiple entries that need to be presented one after
another but the data is not naturally tabular.

```html
{% load panels %}
{% aligned_pair model="episode.start_date | shortDate" label="Start Date" %}
{% aligned_pair model="22" label="Next Data Point" %}
```

Arguments:

* `label`: The left hand item, to be rendered bold.
* `model`: The right hand item, to be rendered as an angular expression

#### {% cached_subrecord_modal subrecord, prefix(optional) %}

Render the subrecords modal inline in an angular ng-template script tag so that it
loads instantaniously for the user.

Arguments:

* `subrecord`: the subrecord to have its modal cached.
* `prefix`: specify a prefix for the modal, if required
