# The OPAL Data model

The OPAL data model allows for patients to have multiple sequential or concurrent
`Episodes of care`. Some information is linked to an `Episode`, some is linked to
a `Patient`.

![Datamodel](../img/OPAL.datamodel.png)

### Patients

A `Patient` may have many `Episodes`. An `Episode` is something like an Inpatient admission, 
a Telephone Liaison, care under an outpatient clinic, an appointment at a drop in clinic.
Applications or plugins may define their own `Episode` types, and a common pattern is to 
alter the display or available functionality by episode type. (e.g. You may associate 
templates for discharge summaries with particular episode types)

A `Patient` will have `Subrecords` (such as e.g. Demographics) which follow them across multiple 
episodes. These are information linked to a particular person, and should be implemented as
Django models that inherit from the `opal.models.PatientSubrecord` base class.

### Episodes

An `Episode` is linked to a `Patient`, and will contain some metadata about the type and date 
of the episode. The field `Episode.category` stores the type of episode ('Inpatient', 'Outpatient', ...)
while the fields `Episode.date_of_admission`, `Episode.discharge_date`, and `Episode.date_of_episode` 
store information about when the `Episode` occurrs.

An `Episode` will have `Subrecords` (such as e.g. Diagnosis) which are linked to this episode of
care. These should be implemented as Django models that inherit from the `opal.models.EpisodeSubRecord`
base class.

### Sub Records

A `Subrecord` consists of a collection of fields that constitute a record. For example, one could 
implement a Demograpics `Subrecord` as follows:

    class Demographics(PatientSubrecord):
        name             = models.CharField(max_length=255, blank=True)
        hospital_number  = models.CharField(max_length=255, blank=True)
        nhs_number       = models.CharField(max_length=255, blank=True, null=True)
        date_of_birth    = models.DateField(null=True, blank=True)
        country_of_birth = ForeignKeyOrFreeText(DestinationLookupList)
        ethnicity        = models.CharField(max_length=255, blank=True, null=True)
        gender           = models.CharField(max_length=255, blank=True, null=True)


Subrecords also define various properties that will provide metadata about their
display or structure, which are documented in the 
(Subrecord reference material)[../reference/subrecords.md]
