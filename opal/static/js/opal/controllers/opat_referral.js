//
// This is our "Enter OPAT" flow controller
// 
controllers.controller(
    'OPATReferralCtrl',
    function($scope, $modalInstance, $modal, $rootScope, $q,
             growl,
             schema, options,
             Episode){
        
        $scope.model = {
            hospital_number : null
        }
        $scope.patient = null;

        //
        // When we've created an episode with this flow, tag it to the correct
        // teams and then kill the modal.
        // 
        $scope.tag_and_close = function(episode){
            if(!episode.newItem){
                episode = new Episode(episode, schema);
            };
            if(!episode.tagging[0].makeCopy){
                episode.tagging[0] = episode.newItem('tagging');
            }
            var teams = episode.tagging[0].makeCopy();
            var location = episode.location[0].makeCopy();
            
            // 
            // See https://github.com/openhealthcare/elcid/issues/484 -
            //
            // Becuase we have a referrals situation, we have to flush teams.
            //
            _.each(_.keys(teams), function(team){
                if(teams[team]){ teams[team] = false };
            })
                
            teams.opat = true;
            teams.opat_referrals = true;
            location.category = 'OPAT';
            location.opat_referral = moment();
            
            //
            // Pre fill some tests:
            //
            var mrsa = episode.newItem('microbiology_test');
            var vte = episode.newItem('microbiology_test');

            $q.all([
                episode.tagging[0].save(teams),
                episode.location[0].save(location),
                mrsa.save({test: 'MRSA PCR'}),
                vte.save({test: 'VTE Assessment'})
            ]).then(function(){
                episode.active = true;
                growl.success("Added " + episode.demographics[0].name)
                $modalInstance.close(episode);
            });                        
        };

        // 
        // We have an initial hospital number - we can now figure out whether to
        // Add or pull over.
        // 
        $scope.find_by_hospital_number = function(){
            Episode.findByHospitalNumber(
                $scope.model.hospital_number,
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
						return { hospital_number: $scope.hospital_number }
					}
				}
			}).result.then(function(result) {
				// The user has created the episode, or cancelled
                if(result){ // We made an episode!
                    $scope.tag_and_close(result);
                }else{
				    $modalInstance.close(result);
                }
			});
        };

        // 
        // Create a new episode for an existing patient
        // 
        $scope.new_for_patient = function(patient){
            if(patient.active_episode_id && _.keys(patient.episodes).length > 0){
                // Offer to import the data from this episode.
				for (var eix in patient.episodes) {
					patient.episodes[eix] = new Episode(patient.episodes[eix], schema);
				};
				modal = $modal.open({
					templateUrl: '/templates/modals/copy_to_category.html/',
					controller: 'CopyToCategoryCtrl',
					resolve: {
                        category: function() { return 'OPAT' },
						patient: function() { return patient; },
					}
				}).result.then(
                    function(result) {
                        if(!_.isString(result)){
                            $scope.tag_and_close(result);
                            return
                        };
					    if (result == 'open-new') {
						    // User has chosen to open a new episode
                            $scope.add_for_patient(patient);
					    } else {
						    // User has chosen to reopen an episode, or cancelled
						    $modalInstance.close(result);
					    };
				    },
                    function(result){ $modalInstance.close(result); });
            }else{
                $scope.add_for_patient(patient);
            };
        };
        
        // 
        // Add a new episode for an existing patient. Pre-fill the relevant demographics
        // 
        $scope.add_for_patient = function(patient){
            var demographics = patient.demographics[0];
            if(demographics.date_of_birth){
                var dob = moment(demographics.date_of_birth, 'YYYY-MM-DD')
                    .format('DD/MM/YYYY');
				demographics.date_of_birth = dob;
            }
			modal = $modal.open({
				templateUrl: '/templates/modals/opat/add_episode.html/',
				controller: 'AddEpisodeCtrl',
				resolve: {
					schema: function() { return schema; },
					options: function() { return options; },
					demographics: function() { return demographics; }
				}
			}).result.then(function(result) {
				// The user has created the episode, or cancelled
                if(result){ // We made an episode!
                    $scope.tag_and_close(result);
                }else{
				    $modalInstance.close(result);
                }
			});                
        };

        // Let's have a nice way to kill the modal.
        $scope.cancel = function() {
	        $modalInstance.close('cancel');
        };        
    }
);
