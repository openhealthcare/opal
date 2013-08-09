// TODO don't hardcode this
var DATE_FIELDS = {
	demographics: ['date_of_birth'],
	location: ['date_of_admission', 'discharge_date'],
	diagnosis: ['date_of_diagnosis'],
	past_medical_history: [],
	general_note: ['date'],
	travel: [],
	antimicrobial: ['start_date', 'end_date'],
	microbiology_input: ['date'],
	todo: [],
	microbiology_test: ['date_ordered'],
}

function transformDatesInResponse(response) {
	var item, items;
	for (var subrecordKey in response) {
		items = response[subrecordKey];
		for (var ix = 0; ix < items.length; ix++) {
			item = items[ix];
			for (var fieldName in item) {
				if (DATE_FIELDS[subrecordKey].indexOf(fieldName) != -1) {
					if (item[fieldName]) {
                                                dt = moment(item[fieldName], 'YYYY-MM-DD');
						item[fieldName] = dt._d;
					}
				}
			}
		}
	}
	return response;
}

var services = angular.module('opal.services', ['ngResource']);

services.factory('Patient', function($resource, $http) {
	return $resource(
		'/patient/:id/',
	       	{id: '@id'},
		{
			get: {
				method: 'GET',
				transformResponse: $http.defaults.transformResponse.concat([transformDatesInResponse])
			},
			query: {
				method: 'GET',
				isArray: true,
				transformResponse: $http.defaults.transformResponse.concat([
					function(response) {
						var newResponse = [];
						angular.forEach(response, function(record) {
							newResponse.push(transformDatesInResponse(record));
						});
						return newResponse;
					}
				])
			}
		}
	);
});

services.factory('SchemaLoader', ['$q', '$http', function($q, $http) {
	return function() {
		var delay = $q.defer();
		$http.get('schema/', {cache: true}).then(function(response) {
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
