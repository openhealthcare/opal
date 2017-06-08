angular.module('opal.services')
    .factory('episodeLoader', function($q, $route,
                                           EpisodeResource,
                                           Episode, recordLoader) {
    return function(episode_id) {
        if(!episode_id){
            episode_id = $route.current.params.id;
        }
	    var deferred = $q.defer();
	    recordLoader.load().then(function(records) {
	        EpisodeResource.get({id: episode_id}, function(resource) {
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
