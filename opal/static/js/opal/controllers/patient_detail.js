angular.module('opal.controllers').controller(
    'PatientDetailCtrl',
    function(
        $rootScope, $scope, $modal, $location, $routeParams,
        Flow, Item,
        patient, options, profile
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
        
        _openEditItemModal = function(item, columnName){
            var modal;

            if(profile.readonly){
                return null;
            };
            $rootScope.state = 'modal';

            var modal_opts = {
                backdrop: 'static',
			    templateUrl: '/templates/modals/' + columnName + '.html/',
                controller: 'EditItemCtrl',
                resolve: {
                    item: function() { return item; },
                    options: function() { return options; },
                    profile: function() { return profile; },
                    episode: function() { return $scope.episode; }
                }
            }

            if(item.size){
                modal_opts.size = item.size;
            }else{
                modal_opts.size = 'lg';
            }

            modal = $modal.open(modal_opts);


            modal.result.then(function(result) {
			    $rootScope.state = 'normal';
		    });
        }

        $scope.editNamedItem = function(name, index){
            var item;
            if ($scope.episode[name][index] && $scope.episode[name][index].columnName) {
                item = $scope.episode[name][index];
            } else {
                item = new Item($scope.episode[name][index], $scope.episode, $rootScope.fields[name]);
                $scope.episode[name][index] = item;
            }
            return _openEditItemModal(item, name)
        };

        $scope.newNamedItem = function(name) {
            var item = $scope.episode.newItem(name, {column: $rootScope.fields[name]});
            if (!$scope.episode[name]) {
                $scope.episode[name] = [];
            }
            return _openEditItemModal(item, name);
        };


	    $scope.dischargeEpisode = function() {
            if(profile.readonly){ return null; };

		    $rootScope.state = 'modal';
            var exit = Flow(
                'exit',
                null,  // Schema ? Not used ? Todo: investigate!
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
