var app = angular.module('opal', [
	 'opal.filters',
	 'opal.services',
	 'opal.directives',
	 'opal.controllers',
	 '$strap.directives',
]);

// See http://stackoverflow.com/questions/8302928/angularjs-with-django-conflicting-template-tags
app.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
});

app.config(function($routeProvider) {
	$routeProvider.
		when('/', {
			controller: 'PatientListCtrl',
			resolve: {
				schema: function(schemaLoader) {
					return schemaLoader;
				},
				patients: function(patientsLoader) {
					return patientsLoader();
				},
				options: function(Options) {
					return Options;
				}
			},
			templateUrl: '/templates/patient_list.html'
		}).when('/patient/:id', {
			controller: 'PatientDetailCtrl',
			resolve: {
				schema: function(schemaLoader) {
					return schemaLoader;
				},
				patient: function(patientLoader) {
					return patientLoader();
				}
			},
			templateUrl: '/templates/patient_detail.html'
		}).when('/search', {
			controller: 'SearchCtrl',
			templateUrl: '/templates/search.html'
		}).otherwise({redirectTo: '/'});
});

app.value('$strapConfig', {
	datepicker: {
		type: 'string',
		format: 'dd/mm/yyyy',
	}
});
