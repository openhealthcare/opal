# Flow hooks in OPAL

OPAL provides various hooks that developers can use to customise behaviour at certain key points in a 
patient's journey through a clinical service - for example when a patient is discharged.

These hooks are associated with verbs `enter`, `exit`.

### The Flow schema

Your application scaffold will have created a file at `./yourapp/flow.py`. This file will contain a variable `flow`, 
which is rendered as the flow schema for your application. Instances are defined as pairs of Angular controllers and
templates used to render them.

    flows = {
        'default': {
            'enter': {
                'controller': 'HospitalNumberCtrl',
                'template'  : '/templates/modals/hospital_number.html/'
            },
            'exit': {
                'controller': 'DischargeEpisodeCtrl',
                'template'  : '/templates/modals/discharge_episode.html/'
            }
        }
    }

### The enter verb

The enter verb is called when a patient is added to a service - for instance by adding a patient to a team list.

It should be an Angular controller that expects to be initialised as a modal.

### The exit verb

The exit verb is called when a patient is added to a service - for instance when we discharge a patient, or end
one phase of a clinical pathway.

It should be an Angular controller that expects to be initialised as a modal.
