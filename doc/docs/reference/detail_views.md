# opal.core.PatientDetailView

PatientDetailViews allow us to define a custom view over either one or many episodes,
available from the main [Patient Detail](../guides/patient_detail_views.md) view.

PatientDetailView inherits from the [discoverable](../guides/discoverable.md) features
`DiscoverableFeature`, `SortableFeature`, `RestrictableFeature`.

## Fields

### PatientDetailView.name

The machine readable name for this view. Should be lower case, and have no spaces.

### PatientDetailView.title

The display name for this view. This is what will display in links to it.

### PatientDetailView.template

The template we should use to render the view when it's active.

### PatientDetailView.order

An integer controlling the order of PatientDetailViews in the episode switcher menu on
the Patient Detail screen is determined by this property. Lower numbers mean higher up.

### Classmethods

#### PatientDetailView.visible_to

Overriding this method will restrict who the view is available to. For instance, we
would implement a superuser only view:

    @classmethod
    def to_user(klass, user):
       return user.is_superuser
