angular.module('opal.services')
    .factory('FilterResource', function($resource) {
        return $resource('/search/filters/:id/', {id: '@id'});
});
