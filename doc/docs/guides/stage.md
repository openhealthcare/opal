# Stage

Episodes in Opal may have a stage. This is a mechanism to chart a patients
flow through a system.

The process of this flow is managed by the [episode category](episode_categories).

The episode category contains a list of stages that an episode can have. It
manages the patients flow through the system via the set_stage method on Episode.
The history is stored.

A patient can have one and only one stage with no end date at a time.
