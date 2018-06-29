var controllers = OPAL.module('opal.controllers', [
	'ngCookies',
	'opal.services',
	'ui.event',
	'ui.bootstrap',
    'ngProgressLite',
    'ui.select'
]);

controllers.controller('RootCtrl', function($scope, $location) {
    $scope.$location = $location;

	$scope.keydown = function(e) {
		$scope.$broadcast('keydown', e);
	};
});
