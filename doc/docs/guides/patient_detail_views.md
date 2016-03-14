# OPAL Patient Detail Views

OPAL provides all patients with a detail view.

The default detail view will allow the user to switch between all of a patient's
[episodes](datamodel.md), as well as editing patient information such as Allergies
for example.

### Template selection

The base template for a patient detail view is `./opal/templates/patient_detail_base.html`,
although you can override or customise that for your application most easily by implementing
a `./templates/patient_detail.html` and customising specific blocks, as the OPAL implementation
simply includes the base template.

Each episode will display using the template appropriate for it's `EpisodeType` - for instance
an `InpatientEpisode` will use `./templates/detail/inpatient.html`. You may [define your own
episode types](../reference/episode_types.md) should you require.

### Record Panels

A frequent pattern when constructing detail views is to render a panel for a particular `Subrecord`
type. The panels templatetag library contains some useful helpers for rendering panels based on
models.

    {% load panels %}
    {% record_panel Diagnosis %}

The above code will render a panel for your episode, including the `Subrecord` detail template for
each instance, and allowing editing, deletion and creation of instances of your `Subrecord`.

You may also consult the Detailed [reference documentation](../reference/panels_templatetags.md) for
Record Panels.

### Custom Patient Detail Views

Sometimes we also need to display information about a patient across multiple episodes, or simlply
a particular view of one episode. For instance, you might like to have a specific view for showing
all of the lab results for a patient, which would be overwhelming were they all displayed in the
episode detail view.

OPAL's PatientDetailView allows you to do just this. To add an additional view to a patient you
simply declare a PatientDetailView class:

    # detail.py
    from opal.core import detail

    class MyCustomView(detail.PatientDetailView):
        name = 'my_custom_view'
        title = 'Special View'
        template = 'detail/my_custom_view.html'


This will then be available in the Patient Detail view in the episode switcher menu. You can
find details of all the various options for PatientDetailViews in the
[reference documentation](../reference/detail_views.md).
