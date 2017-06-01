# The User service

The `User` Service in `opal.services` provides us a way to get information about
users of an application.

## Methods

### User.all()

Fetches all users of the application as a list.

```javascript
User.all().then(function(users){
    console.log(users[0]);
    // -> The first user
})
```

### User.get(id)

Fetch one specific user by ID.

```javascript
User.get(1).then(function(user){
    console.log(user);
    // -> The user with ID 1
});
```
