## Roles & Permissions in Opal

Opal provides some global per-user flags, which are set in the UserProfile model, as well
as more detailed permissions available via roles.

### The UserProfile model

Some global properties about Users are set in the `opal.models.UserProfile`
model.

#### UserProfile._can_extract

Boolean flag to determine whether this user is allowed to download data extracts
from the system

#### UserProfile._force_password_change

Boolean flag to determine whether we would like to force this user to change
their password on their next login. This defaults to `True` when the `User` is
first created.

#### UserProfile._readonly

Boolean flag to determine whether this user has read-only access.

#### UserProfile._restricted_only

Boolean flag to determine whether this user should be only shown teams for which they
have explicitly been given permission to view or whether they should also see the list of
general access teams.

#### UserProfile.get_roles()
Return a dictionary of roles in various contexts for our user

    profile.get_roles() # ->
    {
        'default': ['doctor'],
        'some_research_study': ['Clinical Lead']
    }

#### UserProfile.get_teams()

Return a list of `Team` objects that this user should be allowed to see.

### Roles

A user may be given a particular role. These can be either global - in which case they are
returned in the 'default' section of the roles dict from `get_roles()`, or specific to
a team.
