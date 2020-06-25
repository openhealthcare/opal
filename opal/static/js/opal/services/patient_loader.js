angular.module('opal.services').factory('patientLoader', function(
    $q, $window, $http, $route,
    recordLoader, Patient
){
  return function(patientId) {
    "use strict";
    var deferred = $q.defer();

    // if a patient id isn't passed in, defer to route params
    patientId = patientId || $route.current.params.patient_id;
    if(!patientId){
      deferred.resolve([]);
      return deferred.promise;
    }
    var target = "/api/v0.1/patient/" + patientId + '/';
    var getPatientPromise = $http.get(target);

    $q.all([recordLoader.load(), getPatientPromise]).then(
      function(results){
        var patient = new Patient(results[1].data);
        deferred.resolve(patient);
      },
      function(){
        // handle error better
        $window.alert('Patient could not be loaded');
        deferred.resolve(null);
    });

    return deferred.promise;
  };
});
