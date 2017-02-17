## The PatientSummary service

The `PatientSummary` service in `opal.services` provides us with core
functionality related to interacting with patient search results in the client.


### Constructor

The PatientSummary service is instantiated with the Patient search result data
that comes back from the Patient search JSON API.

    var patient_summary = new PatientSummary(json_data);

