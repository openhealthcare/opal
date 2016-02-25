angular.module('opal.controllers').controller(
    'ReopenEpisodeCtrl', function($scope, $http, $timeout,
                                  $modalInstance, patient, tag, subtag)
    {
	    $scope.episodes = _.values(patient.episodes);
	    $scope.model = {episodeId: 'None'};

        $scope.sortEpisodes = function(e1, e2) {
		    var date1 = e1.date_of_admission;
		    var date2 = e2.date_of_admission;

		    if (angular.isUndefined(date1)) {
			    return -1;
		    } else if (angular.isUndefined(date2)) {
			    return 1;
		    } else if (date1 < date2) {
			    return -1;
		    } else if (date2 < date1) {
			    return 1;
		    } else {
			    return 0;
		    };
	    }

	    $scope.episodes.sort($scope.sortEpisodes);

	    $scope.openNew = function() {
		    $modalInstance.close('open-new');
	    };

	    $scope.reopen = function() {
		    var episode = patient.episodes[parseInt($scope.model.episodeId, 10)];
		    var tagging = episode.getItem('tagging', 0);
		    var attrs = tagging.makeCopy();

		    attrs[tag] = true;
            if(subtag != ''){
                attrs[subtag] = true;
            }
		    tagging.save(attrs).then(function(result) {
                episode.active = true;
			    $modalInstance.close(episode);
		    });
	    };

	    $scope.cancel = function() {
		    $modalInstance.close(null);
	    };

    });
