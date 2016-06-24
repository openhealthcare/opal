angular.module('opal.services')
    .factory('patientListLoader', function($q, $window,
                                           $http,
                                           $route,
                                           Episode,
                                           recordLoader) {
        return function() {
            "use strict";

	        var deferred = $q.defer();
            var params = $route.current.params;
            var target = '/api/v0.1/patientlist/' + params.slug + '/';

            var getEpisodesPromise = $http.get(target);

            $q.all([recordLoader, getEpisodesPromise]).then(function(results){
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
