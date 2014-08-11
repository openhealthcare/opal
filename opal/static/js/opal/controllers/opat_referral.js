//
// This is our "Enter OPAT" flow controller
// 
controllers.controller(
    'OPATReferralCtrl',
    function($scope, $modalInstance, $modal,
             schema, options,
             Episode){
        
        $scope.hospital_number = null;
        $scope.patient = null;
        
        // 
        // We have an initial hospital number - we can now figure out whether to
        // Add or pull over.
        // 
        $scope.find_by_hospital_number = function(){
            Episode.findByHospitalNumber(
                $scope.hospital_number,
                {
                    newPatient: $scope.new_patient,
                    newForPatient: $scope.new_for_patient,
                    error: function(){
			            // This shouldn't happen, but we should probably handle it better
			            alert('ERROR: More than one patient found with hospital number');
                        $modalInstance.close(null)
                    }
                }
            );
        };

        // 
        // Create a new patient
        // 
        $scope.new_patient = function(result){
			// There is no patient with this hospital number
			// Show user the form for creating a new episode,
            // with the hospital number pre-populated
			modal = $modal.open({
				templateUrl: '/templates/modals/opat/add_episode.html/',
				controller: 'AddEpisodeCtrl',
				resolve: {
					schema: function() { return schema; },
					options: function() { return options; },
					demographics: function() {
						return { hospital_number: $scope.hospita_number }
					}
				}
			}).result.then(function(result) {
				// The user has created the episode, or cancelled
                if(result){ // We made an episode!
                    var teams = result.tagging[0].makeCopy();
                    teams.opat_referrals = true;
                    result.tagging[0].save(teams).then(function(){
                        $modalInstance.close(result);
                    });
                }else{
				    $modalInstance.close(result);
                }
			});
        };

        // 
        // Create a new episode for an existing patient
        // 
        $scope.new_for_patient = function(patient){
            // Open an 'internal referral' option.
            //
            // If there is an active episode, duplicate it.
            // If not, create a new episode.
            //
        };

        // Let's have a nice way to kill the modal.
        $scope.cancel = function() {
	        $modalInstance.close('cancel');
        };        
    }
);
