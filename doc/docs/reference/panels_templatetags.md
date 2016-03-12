# Form Helpers

OPAL comes with a selection of templatetags for rendering OPAL panels
for a given subrecord. These panels also allow the user to
see instances of the model against the current value of `episode` in
Angular `$scope`. The user can also create new
instances of the given model, as well as editing any existing ones.

## {% record_panel ... %}

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

## {% record_timeline ... %}

Similar to `record_panel`, `record_timeline` renders a penel for a given record as a timeline - particularly
useful for subrecord types where the date is a key field.

    {% load panels %}
    {% record_panel Diagnosis 'when' %}


Arguments:

* `model`: The model we want to render our panel for
* `whenfield`: String of the field that we're using to sort by.
