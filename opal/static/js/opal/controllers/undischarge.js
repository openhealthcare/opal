angular.module('opal.controllers').controller(
    'UndischargeCtrl',
    function($scope, $modalInstance, episode){

        $scope.episode = episode;

        $scope.confirm = function(){

            $scope.episode.end = null;
            $scope.episode.save(episode.makeCopy()).then(function(){
                var location = $scope.episode.location[0].makeCopy();

                location.category = 'Inpatient';
                $scope.episode.location[0].save(location).then(function(){
                    $modalInstance.close($scope.episode);
                });
            });
        };

        $scope.cancel = function(){
            $modalInstance.close(null);
        };

    }
);
