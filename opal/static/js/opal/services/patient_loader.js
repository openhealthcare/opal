angular.module('opal.services')
    .factory('patientLoader', function($q, $window, $http, $route, Episode, recordLoader ) {
        return function() {
	        var deferred = $q.defer();
            recordLoader.then(function(records){
                var hospitalNumber = $route.current.params.id;

                if(!hospitalNumber){
                    deferred.resolve([])
                }

                target = "/api/v0.1/patient/" + hospitalNumber + '/';

                $http.get(target).then(
                    function(resources) {
                        var patient = resources.data;
                        patient.episodes = _.map(patient.episodes, function(resource) {
                            return new Episode(resource);
                        });
                        deferred.resolve(patient);
                    }, function() {
                        // handle error better
                        $window.alert('Episodes could not be loaded');
                    });
            });
	        return deferred.promise;
        };
    });
