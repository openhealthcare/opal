angular.module('opal.services')
    .factory('episodeLoader', function($q, $route,
                                           EpisodeResource,
                                           Episode, detailSchemaLoader) {
    return function() {
	    var deferred = $q.defer();
	    detailSchemaLoader.then(function(schema) {
	        EpisodeResource.get({id: $route.current.params.id}, function(resource) {
		        var episode = new Episode(resource, schema);
		        deferred.resolve(episode);
	        }, function() {
		        // handle error better
		        alert('Episode could not be loaded');
	        });
	    });
	    return deferred.promise;
    };
});
