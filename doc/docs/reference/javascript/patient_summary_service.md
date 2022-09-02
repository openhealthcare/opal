## The PatientSummary service

The `PatientSummary` service in `opal.services` provides us with core
functionality related to interacting with patient search results in the client.


### Constructor

The PatientSummary service is instantiated with the patient search result data
that comes back from the patient search JSON API.

    var patientSummary = new PatientSummary(json_data);

Whatever is on the JSON response is put onto patientSummary.data. The constructor adds in the below to the object itself:

 * `hospitalNumber`
 * `patientId`
 * `link` A link to the patients patient detail page
 * `dateOfBirth` The patient's date of birth cast to a moment
 * `startDate` The patient's earliest episode.start cast to a moment
 * `endDate` The patient's last episdoe.end cast to a moment
 * `years` The span of years between startDate and EndDate e.g. "2020-2023"
 * `categories` A comma joined string of the patient's episode categories, e.g. "Inpatient, ICU"
