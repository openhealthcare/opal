## The PatientSummary service

The `PatientSummary` service in `opal.services` provides us with core
functionality related to interacting with patient search results in the client.


### Constructor

The PatientSummary service is instantiated with the patient search result data
that comes back from the patient search JSON API.

```javascript
var patientSummary = new PatientSummary(json_data);
```

The result object has the following properties by default:

 * `hospitalNumber`
 * `patientId`
 * `link` A link to the patients patient detail page
 * `dateOfBirth` The patient's date of birth cast to a moment
 * `startDate` The patient's earliest episode.start cast to a moment
 * `endDate` The patient's last episdoe.end cast to a moment
 * `years` The span of years between startDate and EndDate e.g. "2020-2023"
 * `categories` A comma joined string of the patient's episode categories, e.g. "Inpatient, ICU"
 * `data` the raw JSON data from the API
 
