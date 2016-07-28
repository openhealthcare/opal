# Flow hooks in OPAL

OPAL provides various hooks that developers can use to customise behaviour at certain key points in a
patient's journey through a clinical service - for example when a patient is discharged.

These hooks are associated with verbs `enter`, `exit`.

### The Flow service

Your application scaffold will have created a file at
`./yourapp/assets/js/yourapp/services/flow.js`. This file will declare an angular service that
your application will use to determine how to move to the correct next step for a patient.

To enable this, we must set the following setting:

```python
# settings.py
OPAL_FLOW_SERVICE = 'MyAppFlow'
```

Flow services must define an `enter` and an `exit` method, which both return the appropriate
angular controller and template to use. Although OPAL provides sensible default controllers and
templates for these common actions, applications with custom flows may customise these methods
as required.

### The enter verb

The enter verb is called when a patient is added to a service - for instance by adding a patient to a team list.

Implementations of enter are expected to return a dictionary of the controller and template they wish to be called.

    enter: function(){
            return {
                'controller': 'HospitalNumberCtrl',
                'template'  : '/templates/modals/hospital_number.html/'
            }
        }

A common strategy is to examine angular `$route` or `$routeParams` to determine where the user is in the application.
For instance you may wish to have custom controllers for a particular patient list, or the search results page.

### The exit verb

The exit verb is called when a patient is moving through a service - for instance when we discharge a patient, or end
one phase of a clinical pathway.

Implementations of exit are expected to return a dictionary of the controller and template they wish to be called.

The enter verb will receive the episode that we are acting on - for instance a controller that acts differently for
deceased patients might look as follows

    exit: function(episode){
          if(episode.demographics[0].deceased){
              return {
                  'controller': 'DeceasedDischargeEpisodeCtrl',
                  'template'  : '/templates/modals/deceased_discharge.html/'
              }
          }
          return {
              'controller': 'DischargeEpisodeCtrl',
              'template'  : '/templates/modals/discharge_episode.html/'
          }
        }
