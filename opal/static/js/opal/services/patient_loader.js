angular.module('opal.services')
    .factory('patientLoader', function($q, $window, $http, $route, Episode, recordLoader ) {
        return function() {
	        var deferred = $q.defer();
            recordLoader.then(function(records){
                var patient_id = $route.current.params.patient_id;

                if(!patient_id){
                    deferred.resolve([]);
                }

                target = "/api/v0.1/patient/" + patient_id + '/';

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
