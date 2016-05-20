var controllers = OPAL.module('opal.controllers', [
	'ngCookies',
	'opal.services',
	'ui.event',
	'ui.bootstrap',
    'ngProgressLite',
    'mgcrea.ngStrap.typeahead',
    'mgcrea.ngStrap.helpers.dimensions',
    'mgcrea.ngStrap.helpers.parseOptions',
    'mgcrea.ngStrap.tooltip',
    'mgcrea.ngStrap.popover',
    'mgcrea.ngStrap.helpers.dateParser',
    'mgcrea.ngStrap.datepicker',
    'mgcrea.ngStrap.timepicker',
    'ui.select'
]);

controllers.controller('RootCtrl', function($scope, $location) {
    $scope.$location = $location;

	$scope.keydown = function(e) {
		$scope.$broadcast('keydown', e);
	};

    if(typeof collaborator != 'undefined'){ collaborator($scope) };
});

controllers.config(function($datepickerProvider) {
  angular.extend($datepickerProvider.defaults, {
      autoclose: true,
      dateFormat: 'dd/MM/yyyy',
      dateType: 'string'
  });
})
