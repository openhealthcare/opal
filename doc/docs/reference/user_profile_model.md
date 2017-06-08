## opal.models.UserProfile

The model which stores individual user profile information.

### Methods

#### UserProfile.get_avatar_url

Return the URL at which the avatar for this user may be found.
Uses the User email address if it exists or the username to locate a
Gravatar URL.

```python
profile = UserProfile.objects.get(pk=1)
profile.get_avatar_url()
# http://gravatar....
```
