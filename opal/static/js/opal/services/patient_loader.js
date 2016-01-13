angular.module('opal.services')
    .factory('patientLoader', function($q, $window, $http, $route, Episode, recordLoader ) {
        return function() {
          "use strict";
	        var deferred = $q.defer();
            var patient_id = $route.current.params.patient_id;
            if(!patient_id){
                deferred.resolve([]);
            }
            var target = "/api/v0.1/patient/" + patient_id + '/';
            var getEpisodePromise = $http.get(target);


            $q.all([recordLoader, getEpisodePromise]).then(
                    function(results)   {
                        var patient = results[1].data;
                        patient.episodes = _.map(patient.episodes, function(resource) {
                            return new Episode(resource);
                        });
                        deferred.resolve(patient);
                    }, function() {
                        // handle error better
                        $window.alert('Episodes could not be loaded');
              });
	        return deferred.promise;
        };
    });
