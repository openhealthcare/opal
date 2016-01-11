angular.module('opal.controllers').controller(
    'EditTeamsCtrl', function(
        $scope, $modalInstance, $modal, $q, ngProgressLite,
        Options,
        episode) {

        $scope.editing = {};
        
        Options.then(
            function(options){
                $scope.options = options;
                var direct_add = _.filter(options.tag_display, function(v, k){
                    return _.contains(options.tag_direct_add, k);
                });

                $scope.tagging_display_list = _.values(direct_add);
                $scope.display_tag_to_name = _.invert(options.tag_display);
                $scope.episode = episode;

                console.log(episode.tagging[0]);
                $scope.editing.current_tags = _.filter(_.map(
                    $scope.episode.getTags(),
                    function(k){ 
                        if(_.contains(direct_add, $scope.options.tag_display[k])){
                            console.log(k)
                            console.log($scope.options.tag_display[k] )
                            return $scope.options.tag_display[k] 
                        }
                    }));
                console.log($scope.editing.current_tags);

            }            
        );
        
        
        //
        // Save the teams.
        //
	    $scope.save = function(result) {
            ngProgressLite.set(0);
            ngProgressLite.start();
            var new_tags = {};
            _.each($scope.editing.current_tags, function(t){ new_tags[$scope.display_tag_to_name[t]] = true });
            console.log(new_tags)
            $scope.episode.tagging[0].save(new_tags).then(function() {
                ngProgressLite.done();
			    $modalInstance.close(result);
		    });
	    };

        // Let's have a nice way to kill the modal.
	    $scope.cancel = function() {
		    $modalInstance.close('cancel');
	    };

    });
