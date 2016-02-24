angular.module('opal.controllers').controller(
    'PatientDetailCtrl',
    function(
        $rootScope, $scope, $modal, $location, $routeParams,
        Flow, Item, patient, options, profile
    ){
        $scope.profile = profile;
        $scope.patient = patient;
        $scope.options = options;
        $scope.episode = patient.episodes[0];

        $scope.view = null;

        $scope.switch_to_episode = function(index, $event){
            if($event){
                $event.preventDefault()

            }
            $scope.episode = $scope.patient.episodes[index];
            $scope.view = null;
            return true
        }

        $scope.switch_to_view = function(what){
            $scope.view = what;
            return true
        }

        if($routeParams.view){
            if(_.isNaN(parseInt($routeParams.view))){
                $scope.switch_to_view($routeParams.view);
            }else{
                var index = null
                var target = parseInt($routeParams.view);
                _.each($scope.patient.episodes, function(episode, i){
                    if(episode.id == target){
                        index = i;
                    }
                });
                if(index != null){
                    $scope.switch_to_episode(index);
                }
            }
        }

      var recordEditor = new RecordEditor(options, profile);

      self.deleteItem = function(columnName, iix){
          $scope.episode.recordEditor.deleteItem(name, iix, $rootScope);
      };

      $scope.editNamedItem = function(name, iix){
          $scope.episode.recordEditor.editItem(name, iix, $rootScope);
      };

      $scope.newNamedItem = function(name){
          $scope.episode.recordEditor.newItem(name, $scope, $rootScope);
      };


	    $scope.dischargeEpisode = function() {
            if(profile.readonly){ return null; };

		    $rootScope.state = 'modal';
            var exit = Flow(
                'exit',
                options,
                {
                    current_tags: {
                        tag   : $scope.currentTag,
                        subtag: $scope.currentSubTag
                    },
                    episode: $scope.episode
                }
            );

            exit.then(function(result) {
			    $rootScope.state = 'normal';
		    });
	    };

    }
);
