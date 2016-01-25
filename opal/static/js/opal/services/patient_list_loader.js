angular.module('opal.services').factory('patientListLoader', function($http, $q) {
  return function() {
    "use strict";
    var deferred = $q.defer();
    var config = {
      url: "/api/v0.1/patient-list/",
      method: 'GET',
      cache: true
    };

    $http(config).then(function(result){
      deferred.resolve(result.data);
    });

    return deferred.promise;
  };
});
