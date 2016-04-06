angular.module('opal.controllers').controller(
    'EditTeamsCtrl', function(
        $scope, $modalInstance, $modal, $q, ngProgressLite,
        TagService, episode) {

        $scope.editing = {};

        var currentTags = episode.getTags();
        $scope.tagService = new TagService(currentTags);

        //
        // Save the teams.
        //
  	    $scope.save = function(result) {
              ngProgressLite.set(0);
              ngProgressLite.start();
              episode.tagging[0].save($scope.tagService.toSave()).then(function() {
                ngProgressLite.done();
      			    $modalInstance.close(result);
  		    });
  	    };

        // Let's have a nice way to kill the modal.
  	    $scope.cancel = function() {
  		    $modalInstance.close('cancel');
  	    };
    });
