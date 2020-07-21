angular.module('opal.controllers').controller(
    'DeleteItemConfirmationCtrl',
    function($scope, $modalInstance, item) {
    // TODO: Reimplement this!
    //
	// $timeout(function() {
	// 	dialog.modalEl.find('button.btn-primary').first().focus();
	// });

	$scope.destroy = function() {
		item.destroy().then(function() {
			$modalInstance.close('deleted');
		});
	};

	$scope.cancel = function() {
		$modalInstance.close('cancel');
	};
});
