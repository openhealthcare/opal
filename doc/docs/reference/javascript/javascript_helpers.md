## Opal Javascript Helpers

### $rootScope methods

Opal provides some methods on the Angular $rootScope object.

#### open_modal

    $rootScope.open_modal(controller, template, {episode: episode})

Open an arbitrary controller in a modal, passing in the name of the controller,
the url for the template.

You may also pass through a dictionary of items to resolve.

### Angular Directives

Opal provides some built-in Angular directives for your project to use.

#### date-of-birth

Creates an input field that assumes to base field is a moment and handles validation and parsing. It assumes no one is born in the future or is over 150 years old.

#### tag-select

Creates a multi select box where users can remove or add tags. Only tags set as `direct_add` tags can be set here.
This property is set on individual `PatientList` subclasses, and passed to the front end with the `Metadata` service.

We set the Angular model to be a copy of an episode's tagging.

```js
$scope.editing.tagging = episode.tagging[0].makeCopy();
```

We can instantiate the tag-select widget in our markup as follows.

```html
<div tag-select ng-model="editing.tagging" metadata="metadata" class="col-sm-8">
</div>
```

Note: this directive will load the `Metadata` service over HTTP if it has not been loaded already.

#### one-click-only

A directive that if set with no arguments, or set to true, will only allow a button to be
clicked on once and then it'll be disabled. Useful for example to make sure that multiple save requests aren't
accidentally triggered.

#### check-form

Similar to one click only but it takes the form in use as an argument

e.g.
```html
<button check-form="form" ng-click="sendDataToTheServer">click me</button>
```

This checks the form for valid on click.

If the form is then not valid. It will not call the second function, but mark the form as submitted and disable the button.

It will watch for the form to become valid and undisable the button when that happens.

If the form is valid, it will allow the ng-click function to be called.

This means that if you only want to show error messages after the user has clicked the save button you can do so with the
form.$submitted variable.

#### scroll-top

Adds a click handler to the element that when click will animate the body of the element to scroll to the top

#### go-to-top

Similar to scroll-top, this moves the scroll bar to the top of the page but doesn't animate the transition.

#### copy to clipboard

##### e.g.
```html
<button clipboard data-clipboard-target="#content-to-copy">
Copy to Clipboard
</button>
```

This is a wrapper around clipboard.js, it lets the user copy text from an element that matches the selector you pass it. It will present a growl message saying that the text has been
copied.

#### fullNameForUser

Given a User ID, inserts the full name of a user into the element the directive is on

```html
<span full-name-for-user="2"></span>
<!-- Becomes -->
<span>Jane Doe</span>
```

#### avatarForUser

Intended for use on an `img` tag, given a User ID, sets the src attribute to the correct
avatar URL.

```html
<img avatar-for-user="1" />
<!-- Becomes -->
<img src="http://gravatar.com....." />
```

### Angular Filters

Opal provides some built-in Angular filters for your project to use.

#### short-date

Displays a date as DD/MM if it's this year, else DD/MM/YYYY

#### hhmm

Displays the hours & minutes portion of a javascript Date object as HH:MM

#### short-date-time

Displays a date time, short date as above and time as in hhmm above

#### moment-date-filter

Allows a us to use moment.js formatters in the template exactly like you would use moment.format

#### title

Converts a string to title case

#### upper

Converts a string to upper case

#### plural

takes a word, a count, and an optional plural term.

if count != 1 and there is a plural term it will return the plural term otherwise it will just suffix an 's'

if count == 1 then it will return the word

#### age

calculates a persons current age from their date of birth

#### boxed

Displays Boolean fields as a checkbox (e.g. either [ ] or [X])

    [[ item.boolean_field | boxed]]


### Angular HTTP Interceptors

opal uses opal.services.LogoutInterceptor to intercept all failed responses from the server. If they're a 401 or a 403 we redirect the user to the login page, otherwise it passes them through.
