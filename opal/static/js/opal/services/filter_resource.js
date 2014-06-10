angular.module('opal.services')
    .factory('FilterResource', function($resource) {
        return $resource('/filters/:id/', {id: '@id'});
});
