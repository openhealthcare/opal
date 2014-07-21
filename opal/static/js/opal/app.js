var app = angular.module('opal', [
    'ngRoute',
	'opal.filters',
	'opal.services',
	'opal.directives',
	'opal.controllers',
    'ui.bootstrap',
]);

// See http://stackoverflow.com/questions/8302928/angularjs-with-django-conflicting-template-tags
app.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
});

