# Tutorial: Creating forms with Opal

In this section we walk you through creating a simple Pathway.

### Your First Pathway

Pathways are an Opal
[Discoverable feature](discoverable) -
this means that Opal will automatically load any Pathways defined in a python module
named `pathways.py` inside a Django App.

Individual pathways are defined by subclassing a `Pathway` class. You must set at least the
display name, and will
often want to also set a slug.

Out of the box, pathways ships with two types of pathways. A page pathway, a whole bunch of
model forms on the same page, and a wizard pathway, a bunch of steps where the next step is
only revealed after the step before it has been completed.

Let's look at a page pathway definition.

```python
# yourapp/pathways.py
from opal.core import pathway

class MyPathway(pathway.PagePathway):
    display_name = 'My Awesome Pathway'
    slug         = 'awesomest_pathway'
```

### Taking Our First Steps

A Pathway should have at least one `Step` - a section within the form.

`Steps` are defined on the pathway class using the `Pathway.steps` tuple.

```python
from opal.core import pathway
from myapp import models

class SimplePathway(pathway.PagePathway):
    display_name = 'A simple pathway'
    steps        = (
        pathways.Step(model=models.PastMedicalHistory)
    )
```

### Model Steps

A common case is for steps to be simply a single Opal `Subrecord` using the subrecord form template.

In fact we can simply add Opal `Subrecords` to the `steps` tuple to achieve the same effect.

For instance, to create a pathway with three steps to record a
patient's allergies, treatment and past medical history, we could use the following:

```python
from opal.core import pathway
from myapp import models

class SimplePathway(pathway.PagePathway):
    display_name = 'A simple pathway'
    slug         = 'simples'
    steps        = (
        models.Allergies,
        models.Treatment,
        models.PastMedicalHistory
    )
```

Pathways is smart enough to provide a single form step pathway if the model is a [singleton model](../reference/subrecords.md), or a pathway that allows a user to edit/add/remove multiple models if its not a singleton model.


### Viewing The Pathway

This pathway is then available from e.g. `http://localhost:8000/pathway/#/simples`.
