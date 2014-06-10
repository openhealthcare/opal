
angular.module('opal.services')
    .factory('EpisodeResource', function($resource, $q) {
        resource = $resource('/episode/:id/', {id: '@id'});
        return resource
    });
