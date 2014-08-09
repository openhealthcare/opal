//
// This is the "Next stage" exit flow controller for OPAT patients.
//
controllers.controller(
    'OPATDischargeCtrl',
    function($scope, $modalInstance,
             episode, tags){

        var opat_rejection = {
            name: 'opat_rejection',
            fields: [
                {type: 'string', name: 'decided_by'},
                {type: 'string', name: 'reason'},
                {type: 'date', name: 'date'}
            ]
        }

        $scope.episode = episode;
        $scope.meta = {
            accepted: null
        };

        // 
        // The patient is accepted onto the OPAT service.
        // We need to update their tagging data.
        $scope.accept = function(){
            var tagging = $scope.episode.tagging[0].makeCopy();
            tagging.opat_referrals = false;
            tagging.opat_current = true;

            $scope.episode.tagging[0].save(tagging).then(function(){
                $modalInstance.close('moved');
            });
        };

        // 
        // The patient is rejected from the OAPT service.
        // Store some extra data.
        // 
        $scope.reject = function(){
            var reason = $scope.meta.reason;
            var decider = $scope.meta.decider;
            var date = moment().format('YYYY-MM-DD');
            rejection = $scope.episode.newItem('opat_rejection', {column: opat_rejection});
            rejection.save({decided_by: decider, reason: reason, date: date}).then(
                function(){
                    var tagging = $scope.episode.tagging[0].makeCopy();
                    tagging.opat_referrals = false;
                    
                    $scope.episode.tagging[0].save(tagging).then(function(){
                        $modalInstance.close('discharged');
                    });                    
                }
            )
        
            
        };

        // Let's have a nice way to kill the modal.
        $scope.cancel = function() {
	        $modalInstance.close('cancel');
        };
    }
);
