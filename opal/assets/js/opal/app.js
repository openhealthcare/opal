var app = angular.module('opal', [
	'$strap.directives',
	'opal.filters',
       	'opal.services',
       	'opal.directives',
       	'opal.controllers'
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
				schema: function(SchemaLoader) {
					return SchemaLoader();
				},
				patients: function(PatientsLoader) {
					return PatientsLoader();
				}
			},
			templateUrl: '/patient/templates/patient_list.html'
		}).when('/patient/:patientId', {
			controller: 'PatientDetailCtrl',
			resolve: {
				schema: function(SchemaLoader) {
					return SchemaLoader();
				},
				patient: function(PatientLoader) {
					return PatientLoader();
				}
			},
			templateUrl: '/patient/templates/patient_detail.html'
		}).when('/search', {
			controller: 'SearchCtrl',
			templateUrl: '/patient/templates/search.html'
		}).otherwise({redirectTo: '/'});
});

app.value('$strapConfig', {
	datepicker: {
		format: 'dd/mm/yyyy',
		type: 'string'
	}
});

