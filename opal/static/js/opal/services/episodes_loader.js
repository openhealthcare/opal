angular.module('opal.services')
    .factory('episodesLoader', function($q, $window,
                                        $http,
                                        $route,
                                        EpisodeResource, Episode,
                                        listSchemaLoader) {
    return function() {
	    var deferred = $q.defer();
        var params = $route.current.params;

        if(!$route.current.params.tag){
            deferred.resolve([])
        }

	    listSchemaLoader().then(function(schema) {
            var target = '/episode/' + params.tag;
            if(params.subtag){
                target += '/' + params.subtag;
            }
            $http.get(target).then(
                function(resources) {
	                var episodes = {};
		            _.each(resources.data, function(resource) {
		                episodes[resource.id] = new Episode(resource, schema);
		            });
		            deferred.resolve(episodes);
                }, function() {
		            // handle error better
		            $window.alert('Episodes could not be loaded');
	            });
	    });
	    return deferred.promise;
    };
});
