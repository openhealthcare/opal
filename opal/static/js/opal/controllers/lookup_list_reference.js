controllers.controller('LookupListReferenceCtrl', function($scope, $modalInstance, lookuplist_name, lookuplist){
    $scope.lookuplist_name = lookuplist_name;
    $scope.lookuplist = lookuplist;

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

});
