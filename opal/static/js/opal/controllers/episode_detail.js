angular.module('opal.controllers').controller(
    'EpisodeDetailCtrl', function($scope, $modal, $cookieStore, $location,
                                  $rootScope,
                                  Flow, EpisodeDetailMixin,
                                  episode, options, profile) {
        $scope._ = _;
	    $rootScope.state = 'normal';
        $scope.url = $location.url();
        $scope.Flow = Flow;
	    $scope.episode = episode;
        $scope.options = options;
        $scope.profile =  profile;
        $scope.tag_display = options.tag_display;
        $scope.tag_visibile_in_list = options.tag_visibile_in_list;
        EpisodeDetailMixin($scope);
    });
