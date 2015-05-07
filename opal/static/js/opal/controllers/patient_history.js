// 
// This controller displays a patient's episode history 
//
controllers.controller(
    'PatientHistoryCtrl',
    function($scope, $modalInstance, $location, episode){
        $scope.episode = episode;
        $scope.episode_history = angular.copy(episode.episode_history);
        $scope.episode_history.reverse();

        $scope.jump_to_episode = function(episode){
            if(episode.id != $scope.episode.id){
                $location.path('/episode/'+episode.id);
            }
            $scope.cancel();
        }
        
        // Let's have a nice way to kill the modal.
        $scope.cancel = function() {
            $modalInstance.close('cancel');
        };

    }
)
