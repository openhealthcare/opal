//
// This is the "Next stage" exit flow controller for OPAT patients.
//
controllers.controller(
    'OPATDischargeCtrl',
    function($scope, $modalInstance, $rootScope, $q,
             growl,
             Item,
             options, episode, tags){

        var opat_rejection = $rootScope.fields['opat_rejection'];

        $scope.episode = episode;
        $scope.meta = {
            accepted: null,
            rejection: {date: moment().format('YYYY-MM-DD')}
        };

        // Put all of our lookuplists in scope.
	    for (var name in options) {
		    if (name.indexOf('micro_test') != 0) {
			    $scope[name + '_list'] = options[name];
		    };
	    };        

        
        // Make sure that the episode's tagging item is an instance not an object
        $scope.ensure_tagging = function(episode){
            if(!$scope.episode.tagging[0].makeCopy){
                $scope.episode.tagging[0] = $scope.episode.newItem('tagging',{
                    column: $rootScope.fields.tagging }
                                                                  )
            }
            return
        };

        // 
        // This method made more sense when we were storing metadata on a
        // singleton. now it just returns a new metadata instance. 
        // 
        $scope.get_meta = function(){
            return $scope.episode.newItem('opat_meta', {column: $rootScope.fields.opat_meta});
        }
        
        // 
        // The patient is accepted onto the OPAT service.
        // We need to update their tagging data.
        $scope.accept = function(){
            if(!$scope.episode.tagging[0].makeCopy){
                $scope.episode.tagging[0] = $scope.episode.newItem('tagging',{
                    column: {name: 'tagging', fields: [] }
                })
            }
            var tagging = $scope.episode.tagging[0].makeCopy();
            tagging.opat_referrals = false;
            tagging.opat_current = true;
            tagging.opat = true;

            $scope.episode.tagging[0].save(tagging).then(function(){
                growl.success('Accepted: ' + episode.demographics[0].name)
                $modalInstance.close('moved');
            });
        };

        $scope.click_reject = function(){
            $scope.meta.accepted = false;
            $scope.meta.review_date = moment().add(3, 'M')._d;
            return
        }
        // 
        // The patient is rejected from the OAPT service.
        // Store some extra data.
        // 
        $scope.reject = function(){
            var meta = $scope.get_meta();
            var opatmetadata = meta.makeCopy();
            var rejection = $scope.episode.newItem('opat_rejection', {column: opat_rejection});
            var tagging = $scope.episode.tagging[0].makeCopy();

            $scope.ensure_tagging(episode);
            opatmetadata.review_date = $scope.meta.review_date;
            
            tagging.opat_referrals = false;
            tagging.opat = false;                       
            
            $q.all([
                rejection.save($scope.meta.rejection),
                $scope.episode.tagging[0].save(tagging),
                meta.save(opatmetadata)
            ]).then(function(){
                // Doesn't auto update for OPAT as TAGGING is not in the default schema.
                $scope.episode.tagging[0] = tagging; 
                growl.success('Rejected: ' + episode.demographics[0].name)
                $modalInstance.close('discharged');                
            });

        };

        //
        // The patient is being removed from the current list because they've
        // switched to oral antibiotics
        // 
        $scope.switch_to_oral = function(){
            var meta = $scope.get_meta();
            $scope.ensure_tagging($scope.episode);
            var tagging = $scope.episode.tagging[0].makeCopy();
            tagging.opat_current = false;
            tagging.opat_followup = true;

            updatedmeta = meta.makeCopy();
            updatedmeta.reason_for_stopping = $scope.meta.reason;
            updatedmeta.unplanned_stop_reason = $scope.meta.unplanned_stop;
            updatedmeta.stopping_iv_details = $scope.meta.details;

            // Now let's save
            meta.save(updatedmeta).then(function(){
                $scope.episode.tagging[0].save(tagging).then(function(){
                    growl.success('Switched to Oral: ' + episode.demographics[0].name)
                    $modalInstance.close('discharged');
                });
            });
        }

        // 
        // A patient has completed their OPAT therapy.
        // 
        $scope.completed_therapy = function(){
            var meta = $scope.get_meta();
            $scope.ensure_tagging($scope.episode);
            var tagging = $scope.episode.tagging[0].makeCopy();
            tagging.opat_current = false;
            tagging.opat_followup = false;
            
            
            updatedmeta = meta.makeCopy();
            
            updatedmeta.review_date = $scope.meta.review_date;
            updatedmeta.treatment_outcome = $scope.meta.outcome;
            updatedmeta.deceased = $scope.meta.died;
            updatedmeta.cause_of_death = $scope.meta.cause_of_death;
            updatedmeta.death_category = $scope.meta.death_category;
            updatedmeta.readmitted = $scope.meta.readmitted;
            updatedmeta.treatment_outcome = $scope.meta.outcome;
            updatedmeta.notes = $scope.meta.notes;
            
            // Now let's save
            meta.save(updatedmeta).then(function(){
                $scope.episode.tagging[0].save(tagging).then(function(){
                    growl.success('Completed treatment: ' + episode.demographics[0].name)
                    $modalInstance.close('discharged');
                });
            });            
        };

        //
        // The patient is being removed from the follow up list because they're
        // going back to IV
        // 
        $scope.back_to_iv = function(){
            var meta = $scope.get_meta();
            $scope.ensure_tagging($scope.episode);
            var tagging = $scope.episode.tagging[0].makeCopy();
            tagging.opat_current = true;
            tagging.opat_followup = false;
            updatedmeta = meta.makeCopy();
            updatedmeta.reason_for_stopping = $scope.meta.reason;
            updatedmeta.unplanned_stop_reason = $scope.meta.unplanned_stop;
            updatedmeta.stopping_iv_details = $scope.meta.details;

            // Now let's save
            meta.save(updatedmeta).then(function(){
                $scope.episode.tagging[0].save(tagging).then(function(){
                    growl.success('Moved back to IVs: ' + episode.demographics[0].name)
                    $modalInstance.close('discharged');
                });
            });
        }
        
        
        // Let's have a nice way to kill the modal.
        $scope.cancel = function() {
	        $modalInstance.close('cancel');
        };
    });
