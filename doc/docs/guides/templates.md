OPAL uses a mixture of Django and Angular templates.

### Angular templates 

In order to be compatible with Django templating, we use the `[[ ... ]]` notation for
Angular interpolation, which allows us to mix Django template interpolation in templates
designed to be rendered by Angular on the client side.

    <!-- app_details_snippet.html -->
    {{ OPAL_BRAND_NAME }} [[ OPAL_VERSION ]]

### Generic Template URL

On many occasions we simply want to fetch a template from the server in our Angular code
without any further processing. OPAL provides a default catchall HTML template url which
will render .html files direct from disk.

    # opal.urls

    url(r'templates/(?P<template_name>[a-z_/]+.html)', views.RawTemplateView.as_view())

So if our template is at `./myapp/templates/foo/bar.html`, then the url `/templates/foo/bar.html`
will return it.

### Partials

OPAL has some built in template partials that are generally useful.

##### partials/_episode_summary_table.html

A table that renders the name, hospital number, date of birth, date of admission & discharge date
for a list of episodes. Expects episodes to be stored in `$scope.results`. Will limit the 
number of results to `$scope.limit` .Clicking on an individual 
episode in the table will call `$scope.jumpToEpisode(episode)`.

    // Controller Fn
    function($scope, episodes, $location){
        $scope.limit = 10;
        $scope.results = episodes;
        $scope.jumpToEpisode = function(episode){ $location.path('/episode/'+episode.id }
    }
