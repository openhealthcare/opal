angular.module('opal.controllers').controller(
    'EpisodeDetailCtrl', function($scope, $modal, $cookieStore, $location,
                                  $rootScope,
                                  Flow, EpisodeDetailMixin,
                                  schema,
                                  episode, options, profile) {
        $scope._ = _;
	    $scope.state = 'normal';

	    $scope.cix = 0; // column index
	    $scope.iix = 0; // item index

	    $scope.mouseCix = -1; // index of column mouse is currently over

        $scope.Flow = Flow;
	    $scope.episode = episode;
        $scope.options = options;
        $scope.schema = schema;
        $scope.total_episodes = 1 + episode.prev_episodes.length + episode.next_episodes.length;
        $scope.this_episode_number = episode.prev_episodes.length + 1;
        $scope.historyCollapsed = true;

        $scope.profile =  profile;

	    $scope.columns = schema.columns;
        $scope.tag_display = options.tag_display;

        EpisodeDetailMixin($scope);
        
	    $scope.$on('keydown', function(event, e) {
		    if ($scope.state == 'normal') {
			    switch (e.keyCode) {
			    case 38: // up
				    $scope.goUp();
				    break;
			    case 40: // down
				    $scope.goDown();
				    break;
			    case 13: // enter
			    case 113: // F2
				    $scope.editItem($scope.cix, $scope.iix);
				    break;
			    case 8: // backspace
				    e.preventDefault();
			    case 46: // delete
				    $scope.deleteItem($scope.cix, $scope.iix);
				    break;
			    };
		    };
	    });

    });
