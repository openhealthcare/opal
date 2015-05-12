OPAL Subrecords are models that relate to either Patients or Episodes, and inherit from
`opal.models.Subrecord`

## Methods

### Subrecord.get_display_template()

Classmethod to locate the active display templte for our record.

Returns the name of the template or None.

Keywords:

* `team` Optional team to check for form customisations
* `subteam` Optional subteam to check for form customisations


### Subrecord.get_form_template()

Classmethod to locate the active template for our record. Returns the name of a template or None.

Keywords: 

* `team` Optional team to check for form customisations
* `subteam` Optional subteam to check for form customisations
