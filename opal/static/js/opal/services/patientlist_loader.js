angular.module('opal.services')
    .factory('patientListLoader', function($q,
                                           $http,
                                           $route,
                                           Episode,
                                           recordLoader) {
        return function(slug) {
            "use strict";

  	        var deferred = $q.defer();
            if(!slug){
              slug = $route.current.params.slug;
            }
            var target = '/api/v0.1/patientlist/' + slug + '/';

            var getEpisodesPromise = $http.get(target);

            $q.all([recordLoader.load(), getEpisodesPromise]).then(function(results){
                // record loader updates the global scope
                var episodesResult = results[1];
                var episodes = {};
                _.each(episodesResult.data, function(resource) {
                    episodes[resource.id] = new Episode(resource);
                });
                deferred.resolve({status: 'success', data: episodes});
            }, function(resource) {
                deferred.resolve({status: 'error', data: resource.data});
            });

	        return deferred.promise;
        };
    });
