# Opal Episode Detail Views

By defualt, the OPAL core provides each [episode](datamodel.md) with a detail view.

### Template selection

Episode detail templates live in `./templates/detail/*`. In order to select the appropriate
template for a given episode, OPAL looks first for the template for the episode category - so
for `inpatient` episodes, that would be  `detail/inpatient.html`.

The default template is `detail/default.html`.
