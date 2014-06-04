angular.module('opal.controllers')
    .controller('SaveFilterCtrl', function($scope, $modalInstance, Filter, params) {
    $scope.state = 'editing';
    $scope.model = params;

	$scope.save = function(result) {
        $scope.state = 'saving';
        var filter = new Filter($scope.model);
		filter.save($scope.model).then(function(result) {
			$modalInstance.close(result);
		});
	};


	$scope.cancel = function() {
		$modalInstance.close('cancel');
	};

})
