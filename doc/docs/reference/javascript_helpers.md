## OPAL Javascript Helpers

### $rootScope methods

OPAL provides some methods on the Angular $rootScope object.

#### open_modal

    $rootScope.open_modal(controller, template, size, {episode: episode})

Open an arbitrary controller in a modal, passing in the name of the controller,
the url for the template, the size of the modal window (either 'sm' or 'lg').

You may also pass through a dictionary of items to resolve.

### Angular Filters

OPAL provides some buit-in Angular filters for your project to use.

#### shortDate

Displays a date as DD/MM if it's this year, else DD/MM/YYYY

#### hhmm 

Displays the hours & minutes portion of a javascript Date object as HH:MM

