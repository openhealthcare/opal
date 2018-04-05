angular.module('opal.controllers').controller('KeyBoardShortcutsCtrl', function ($scope, $modalInstance) {
  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
});
