
//
// This controller handles internal referrals to the opat service
//
controllers.controller(
    'CopyToCategoryCtrl',
    function($scope, $modalInstance,
             CopyToCategory,
             patient, category_name){

        $scope.patient = patient;

        //
        // Open the episode in a new window.
        //
        $scope.jump_to_episode = function(episode_id){
            window.open('#/episode/'+episode_id, '_blank');
        }

        //
        // The user has decided to open a new episode.
        //
        $scope.open_new = function(){
            $modalInstance.close('open-new');
        };

        //
        // The user has decided to import an existing inpatient episde
        //
        $scope.import_existing = function(){
            CopyToCategory($scope.patient.active_episode_id, category_name).then(
                function(episode){
                    $modalInstance.close(episode);
                },
                function(episode){
                    $modalInstance.close(episode);
                }
            )
        };

        // Let's have a nice way to kill the modal.
        $scope.cancel = function() {
	        $modalInstance.close('cancel');
        };
    });
