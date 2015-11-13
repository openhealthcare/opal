# The record_panel templatetag.

Render a panel for a given record that will allow the user to view, create, update and delete instances.

The record panel template expects the relevant Angular `$scope` to have `newNamedItem(name, index)`, 
`editNamedItem(name, index)` and `deleteNamedItem(name, index)` methods implemented. Default 
implementations of these are available from the `EpisodeDetailMixin`.

    {% load panels %}
    {% record_panel Diagnosis %}

Keywords: 

* `name`: The programatic name for this model.
* `title`: The display title for this panel
* `detail_template`: The display template to use. Defaults to Subrecord.get_detail_template()
* `editable`: Whether this panel should allow editing. Defaults to True.
