// TODO:
// Make sure all modals now have error handlers.
//
var controllers = angular.module('opal.controllers', [
	'ngCookies',
	'opal.services',
	'ui.event',
	'ui.bootstrap',
    'mgcrea.ngStrap.typeahead',
    'mgcrea.ngStrap.helpers.dimensions',
    'mgcrea.ngStrap.tooltip',
    'mgcrea.ngStrap.helpers.dateParser',
    'mgcrea.ngStrap.datepicker',
]);

controllers.controller('RootCtrl', function($scope) {
	$scope.keydown = function(e) {
		$scope.$broadcast('keydown', e);
	};
});
