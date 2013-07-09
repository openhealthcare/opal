var services = angular.module('opal.services', ['ngResource']);

services.factory('Patient', ['$resource', function($resource) {
	return $resource('/patient/:id/', {id: '@id'});
}]);

services.factory('SchemaLoader', ['$q', '$http', function($q, $http) {
	return function() {
		var delay = $q.defer();
		$http.get('schema/').then(function(response) {
			delay.resolve(response.data);
		}, function() {
			delay.reject('There was a problem fetching the schema');
		});		
		return delay.promise;
	};
}]);

services.factory('PatientsLoader', ['Patient', '$q', function(Patient, $q) {
	return function() {
		var delay = $q.defer();
		Patient.query(function(patients) {
			delay.resolve(patients);
		}, function() {
			delay.reject('There was a problem fetching records');
		});
		return delay.promise;
	};
}]);

services.factory('PatientLoader', ['Patient', '$route', '$q', function(Patient, $route, $q) {
	return function() {
		var delay = $q.defer();
		Patient.get({id: $route.current.params.patientId}, function(patient) {
			delay.resolve(patient);
		}, function() {
			delay.reject('There was a problem fetching record '  + $route.current.params.patientId);
		});
		return delay.promise;
	};
}]);
