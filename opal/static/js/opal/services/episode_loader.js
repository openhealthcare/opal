angular.module('opal.services')
    .factory('episodeLoader', function($q, $route,
                                           EpisodeResource,
                                           Episode, recordLoader) {
    return function() {
	    var deferred = $q.defer();
	    recordLoader.then(function(records) {
	        EpisodeResource.get({id: $route.current.params.id}, function(resource) {
		        var episode = new Episode(resource);
		        deferred.resolve(episode);
	        }, function() {
		        // handle error better
		        alert('Episode could not be loaded');
	        });
	    });
	    return deferred.promise;
    };
});
