controllers.controller(
    'DischargeEpisodeCtrl',
    function($scope, $timeout,
             $modalInstance, episode,
             tags) {

        if(tags && !_.isEmpty(tags)){
            $scope.currentTag = tags.tag;
            $scope.currentSubTag = tags.subtag;
        }else{
            $scope.currentTag = 'mine';
            $scope.currentSubTag = '';
        }

        $scope.currentCategory = episode.location[0].category;
        var newCategory;

        if ($scope.currentCategory == 'Inpatient') {
	        newCategory = 'Discharged';
        } else if ($scope.currentCategory == 'Review' ||
                   $scope.currentCategory == 'Followup') {
	        newCategory = 'Unfollow';
        } else {
	        newCategory = $scope.currentCategory;
        }

        $scope.editing = {
	        category: newCategory,
            discharge_date: null
        };

        $scope.episode = episode.makeCopy();
        if(!$scope.episode.end){
          $scope.editing.end = moment().format('DD/MM/YYYY');
        }
        else{
          $scope.editing.end = $scope.episode.end
        }

        //
        // Discharging an episode requires updating three server-side entities:
        //
        // * Location
        // * Tagging
        // * Episode
        //
        // Make these requests then kill our modal.
        //
        $scope.discharge = function() {

	        var tagging = episode.getItem('tagging', 0);
            var location = episode.getItem('location', 0);

	        var taggingAttrs = tagging.makeCopy();
            var locationAttrs = location.makeCopy();
            var episodeAttrs = episode.makeCopy();

	        if ($scope.editing.category != 'Unfollow') {
	            locationAttrs.category = $scope.editing.category;
	        }

            if($scope.editing.category == 'Unfollow') {
                // No longer under active review does not set a discharge date
                episodeAttrs.end = null;
            }

	        if ($scope.editing.category != 'Followup') {
                if($scope.currentSubTag != ''){
                    taggingAttrs[$scope.currentSubTag] = false;
                }else{
                    taggingAttrs[$scope.currentTag] = false;
                }
	        }
	        tagging.save(taggingAttrs).then(function(){
                location.save(locationAttrs).then(function(){
                    episode.save(episodeAttrs).then(function(){
                        $modalInstance.close('discharged');
                    })
                })

	        });
        };

        $scope.cancel = function() {
	        $modalInstance.close('cancel');
        };
    });
