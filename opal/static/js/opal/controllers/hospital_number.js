angular.module('opal.controllers').controller(
    'HospitalNumberCtrl',
    function($scope,
             $timeout,
             $modal,
             $modalInstance,
             $http,
             $q,
             Episode,
             schema,
             options,
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
			            alert('ERROR: More than one patient found with hospital number');
                        $modalInstance.close(null)
                    }
                }
            );

	    };

        $scope.newPatient = function(result){
			// There is no patient with this hospital number
			// Show user the form for creating a new episode,
            // with the hospital number pre-populated
			modal = $modal.open({
				templateUrl: '/templates/modals/add_episode.html/',
				controller: 'AddEpisodeCtrl',
				resolve: {
					schema: function() { return schema; },
					options: function() { return options; },
					demographics: function() {
						return { hospital_number: result.hospitalNumber }
					}
				}
			}).result.then(function(result) {
				// The user has created the episode, or cancelled
				$modalInstance.close(result);
			});
        };

        $scope.newForPatient = function(patient){
			if (patient.active_episode_id && 
                // Check to see that this episode is not "Discharged"
                patient.episodes[patient.active_episode_id].location[0].category != 'Discharged') {
				// This patient has an active episode
                $scope.newForPatientWithActiveEpisode(patient);
			} else { // This patient has no active episode
                // Check to see if the patient has *any* episodes
                if (_.keys(patient.episodes).length ==  0){
                    $scope.addForPatient(patient);
                }else {
					// Convert episodes to Episodes - TODO
                    // it'd be better if this happened when the patient
                    // was retrieved
					for (var eix in patient.episodes) {
						patient.episodes[eix] = new Episode(patient.episodes[eix],
                                                            schema);
					}
					// Ask user if they want to reopen an episode, or open a new one
					modal = $modal.open({
						templateUrl: '/templates/modals/reopen_episode.html/',
						controller: 'ReopenEpisodeCtrl',
						resolve: {
							patient: function() { return patient; },
							tag: function() { return $scope.tags.tag; }
						}
					}).result.then(function(result) {
						var demographics;
						if (result == 'open-new') {
							// User has chosen to open a new episode
                            $scope.addForPatient(patient);
						} else {
							// User has chosen to reopen an episode, or cancelled
							$modalInstance.close(result);
						};
					},
                                   function(result){
                                       $modalInstance.close(result);
                                   });
                }
			};
        };

        $scope.newForPatientWithActiveEpisode = function(patient){
			episode = new Episode(patient.episodes[patient.active_episode_id],
                                  schema)
			if (episode.tagging[0][$scope.tags.tag] &&
                ($scope.tags.subtag == 'all' ||
                 episode.tagging[0][$scope.tags.subtag])) {
				// There is already an active episode for this patient
                // with the current tag
				$modalInstance.close(episode);
			} else {
				// There is already an active episode for this patient but
                // it doesn't have the current tag.
                // Add the current Tag.
                episode.tagging[0][$scope.tags.tag] = true;
                if($scope.tags.subtag != 'all'){
                    episode.tagging[0][$scope.tags.subtag] = true;
                }
                episode.tagging[0].save(episode.tagging[0].makeCopy()).then(
                    function(){
				        $modalInstance.close(episode);
                    });
			}
        };

        $scope.addForPatient = function(patient){
            demographics = patient.demographics[0];
            if(demographics.date_of_birth){
                var dob = moment(demographics.date_of_birth, 'YYYY-MM-DD')
                    .format('DD/MM/YYYY');
				demographics.date_of_birth = dob;
            }

            modal = $modal.open({
				templateUrl: '/templates/modals/add_episode.html/',
				controller: 'AddEpisodeCtrl',
				resolve: {
					schema: function() { return schema; },
					options: function() { return options; },
					demographics: function() { return demographics; }
				}
			}).result.then(
                function(result){
                    $modalInstance.close(result);
                },
                function(result){
                    $modalInstance.close(result);
                });
        };

	    $scope.cancel = function() {
		    $modalInstance.close(null);
	    };

    });
