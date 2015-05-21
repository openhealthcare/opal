# Teams 

Episodes of care are assigned to n teams - broadly a tab in the list view.

Teams are a two level hierarchy currently used to define both clinical services, and stages within a
clinical service.

The common case is that a team represents a clincal service e.g. `Infectious Disieases` or `Renal`, 
while a sub-team might represent e.g. Infectious Diseases `Inpatients` or `Outpatients`.

Teams may be inactive, in which case they are not displayed.

Teams may be restricted in which they only appear for a subset of users.

The logic for showing restricted teams is implemented via plugins.

Teams are assigned to episodes via a `Tagging`
