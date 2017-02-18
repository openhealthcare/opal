angular.module('opal.services').factory('patientLoader', function(
    $q, $window, $http, $route,
    recordLoader, FieldTranslater, Patient
) {
    return function() {
        "use strict";
	    var deferred = $q.defer();
        var patient_id = $route.current.params.patient_id;
        if(!patient_id){
            deferred.resolve([]);
            return deferred.promise;
        }
        var target = "/api/v0.1/patient/" + patient_id + '/';
        var getPatientPromise = $http.get(target);


        $q.all([recordLoader, getPatientPromise]).then(
            function(results)   {
                var patient = new Patient(results[1].data);
                deferred.resolve(patient);
            },
            function() {
                // handle error better
                $window.alert('Patient could not be loaded');
                deferred.resolve();
            });
	    return deferred.promise;
    };
});
