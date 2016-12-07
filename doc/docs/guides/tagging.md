# Tagging

Episodes in Opal may be tagged. This is commonly used as a mechanism to
record that a particular team is looking after a patient - via `TaggedPatientList`,
but also to group patients.

For instance, we might like to 'tag' episodes with a particular string when some
particular event occurrs so that we can run reports or analyse these groups later.

The "Teams" modal in list and detail views, is actually an interface over updating
the tagging of the episode in question.

Metadata concerning tags can be found via the Options API.
