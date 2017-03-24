controllers.controller(
    'AlertCtrl',
    function($scope, $modalInstance, title, message, dismiss_text){
        $scope.title = title;
        $scope.message = message;
        $scope.dismiss_text = dismiss_text;

        $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
        };

    });
