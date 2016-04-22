angular.module('opal.controllers')
    .controller('AddEpisodeCtrl', function($scope, $http,
                                           $timeout, $routeParams,
                                           $modalInstance, $rootScope,
                                           Episode,
                                           TagService,
                                           options,
                                           demographics,
                                           tags) {
      var DATE_FORMAT = 'DD/MM/YYYY';
      var currentTags = [];

	    for (var name in options) {
		    $scope[name + '_list'] = options[name];
	    };

	    $scope.editing = {
        tagging: [{}],
		    location: {},
        demographics: demographics
	    };

      if(tags.tag){
        currentTags = [tags.tag];
      }

      if(tags.subtag){
        // if there's a subtag, don't tag with the parent tag
        currentTags = [tags.subtag];
      }

      $scope.tagService = new TagService(currentTags);

	    $scope.save = function() {
		    var dob, doa;

		    // This is a bit mucky but will do for now
		    doa = $scope.editing.date_of_admission;
        $scope.editing.tagging = [$scope.tagService.toSave()];

        var toSave = angular.copy($scope.editing);


		    if(doa){
            if(!angular.isString(doa)){
                doa = moment(doa).format(DATE_FORMAT);
            }
    			  toSave.date_of_admission = doa;
		    }

        if($scope.editing.demographics.date_of_birth){
            toSave.demographics.date_of_birth = $scope.editing.demographics.date_of_birth.format(
                DATE_FORMAT
            );
        }

		    $http.post('episode/', toSave).success(function(episode) {
			    episode = new Episode(episode);
			    $modalInstance.close(episode);
		    });
	    };

	    $scope.cancel = function() {
		    $modalInstance.close(null);
	    };

    });
