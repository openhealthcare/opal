# The OPAL Data model

The basic data model in OPAL consists of the following hierarchy 

// TODO: Diagram please

Patients have many episodes of care. 
Patients may have sub-records (such as demographics) which follow them across 
multiple episodes.
Episodes also have sub-records (such as diagnosis).

Sub records may either be a 1-1 relationship with their parent, or 1-many.
(e.g. a patient may have exactly one demographics, but many allergies).
