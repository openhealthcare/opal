## opal.models.Team

### Fields

#### name

The slug version of the team name to be used in urls and schemas.

Should only have letters and underscores

#### title

The human facing title of this Team

#### parent

ForeignKey to this Team's parent if one exists

#### active

Boolean to determine whether this Team is active.

Default = True

#### order 

Integer that allows admin users to set the ordering of teams.

#### restricted

Boolean field to indicate that this team is restricted to only a subset of users.

Default = False

#### direct_add

Boolean field to indicate whether we should show this field in the Teams modal.

### Class Methods

#### restricted_teams

Given a user, return the restricted teams this user can access.

    Team.restricted_teams(user)

#### for_user

Return the set of teams this user has access to.

    Team.for_user(user)

### Properties

#### has_subteams

Boolean that is True if this Team has Subteams.
