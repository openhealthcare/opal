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
    'mgcrea.ngStrap.helpers.parseOptions',
    'mgcrea.ngStrap.tooltip',
    'mgcrea.ngStrap.helpers.dateParser',
    'mgcrea.ngStrap.datepicker',
]);

controllers.controller('RootCtrl', function($scope, $location) {
    $scope.$location = $location;
    
	$scope.keydown = function(e) {
		$scope.$broadcast('keydown', e);
	};
});



controllers.config(function($datepickerProvider) {
  angular.extend($datepickerProvider.defaults, {
      autoclose: true,
      dateFormat: 'dd/MM/yyyy',
      dateType: 'string'
  });
})
