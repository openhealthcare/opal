
angular.module('opal.services')
    .factory('EpisodeResource', function($resource) {
        resource = $resource('/api/v0.1/episode/:id/', {id: '@id'});
        return resource
    });
