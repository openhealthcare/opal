angular.module('opal.controllers').controller(
    'HospitalNumberCtrl',
    function($scope,
             $timeout,
             $modal,
             $modalInstance,
             $http,
             $q,
             $window,
             Episode,
             tags,
             hospital_number) {

        $scope.model = {}
        if(hospital_number){
            $scope.model.hospitalNumber = hospital_number;
        }
        $scope.tags = tags;

	    $scope.findByHospitalNumber = function() {

            Episode.findByHospitalNumber(
                $scope.model.hospitalNumber,
                {
                    newPatient: $scope.newPatient,
                    newForPatient: $scope.newForPatient,
                    error: function(){
  			            // This shouldn't happen, but we should probably handle it better
  			            $window.alert('ERROR: More than one patient found with hospital number');
                          $modalInstance.close(null)
                    }
                }
            );

	    };
        var addPatient = function(demographics){
            modal = $modal.open({
  				templateUrl: '/templates/modals/add_episode.html',
  				controller: 'AddEpisodeCtrl',
  				resolve: {
  					referencedata: function(Referencedata) {
                        return Referencedata.load();
                    },
  					demographics: function() {
  						return demographics
  					},
                    tags: function(){ return $scope.tags; }
  				}
  			}).result.then(function(result) {
  				// The user has created the episode, or cancelled
  				$modalInstance.close(result);
  			});
        }

        $scope.newPatient = function(result){
            addPatient({ hospital_number: result.hospitalNumber });
        };

        $scope.addForPatient = function(patient){
            demographics = patient.demographics[0];
            if(demographics.date_of_birth){
                var dob = moment(demographics.date_of_birth, 'YYYY-MM-DD')
                    .format('DD/MM/YYYY');
                demographics.date_of_birth = dob;
            }

            addPatient(demographics);
        };

        $scope.newForPatient = function(patient){
			if (patient.active_episode_id &&
                // Check to see that this episode is not "Discharged"
                patient.episodes[patient.active_episode_id].location[0].category != 'Discharged') {
				// This patient has an active episode
                $scope.newForPatientWithActiveEpisode(patient);
			} else { // This patient has no active episode
                $scope.addForPatient(patient);
			};
        };

        $scope.newForPatientWithActiveEpisode = function(patient){
			episode = new Episode(patient.episodes[patient.active_episode_id])

            if(episode.category_name != 'Inpatient'){ // It's the wrong category - add new
                return $scope.addForPatient(patient);
            }

			if (episode.tagging[0][$scope.tags.tag] &&
                ($scope.tags.subtag == '' ||
                 episode.tagging[0][$scope.tags.subtag])) {
				// There is already an active episode for this patient
                // with the current tag
				$modalInstance.close(episode);
			} else {
				// There is already an active episode for this patient but
                // it doesn't have the current tag.
                // Add the current Tag.
                episode.tagging[0][$scope.tags.tag] = true;
                if($scope.tags.subtag != ''){
                    episode.tagging[0][$scope.tags.subtag] = true;
                }

                episode.tagging[0].save(episode.tagging[0].makeCopy()).then(
                    function(){
				        $modalInstance.close(episode);
                    });
			}
        };



	    $scope.cancel = function() {
		    $modalInstance.close(null);
	    };

    });
