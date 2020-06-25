angular.module('opal.controllers').controller(
    'EditTeamsCtrl', function(
        $scope, $modalInstance, ngProgressLite, episode, UserProfile) {

        UserProfile.load().then(function(profile){
            $scope.editingName = episode.getFullName();
          $scope.profile = profile;
        })


        if(episode.tagging.length){
          $scope.editing = {tagging: episode.tagging[0].makeCopy()};
        }
        else{
          $scope.editing.tagging = {};
        }

        //
        // Save the teams.
        //
  	    $scope.save = function(result) {
            ngProgressLite.set(0);
            ngProgressLite.start();
            episode.tagging[0].save($scope.editing.tagging).then(
                function() {
                    ngProgressLite.done();
      			    $modalInstance.close(result);
  		        },
                function() {
                    ngProgressLite.done();
                }
            );
  	    };

        // Let's have a nice way to kill the modal.
  	    $scope.cancel = function() {
  		    $modalInstance.close('cancel');
  	    };
    });
