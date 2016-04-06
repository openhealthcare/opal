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
	    $scope.currentTag    = tags.tag;
	    $scope.currentSubTag = tags.subtag;

	    for (var name in options) {
		    $scope[name + '_list'] = options[name];
	    };

	    $scope.editing = {
            tagging: [{}],
		    location: {

		    },
		    demographics: demographics
	    };

      if($scope.currentSubTag.length){
        currentTags = [$scope.currentSubTag];
      }
      else{
        currentTags = [$scope.currentTag];
      }

      $scope.tagService = new TagService(currentTags);

	    $scope.save = function() {
		    var dob, doa;

		    // This is a bit mucky but will do for now
		    doa = $scope.editing.date_of_admission;
        $scope.editing.tagging = [$scope.tagService.toSave()];
		    if (doa) {
                if(!angular.isString(doa)){
                    doa = moment(doa).format(DATE_FORMAT);
                }
			    $scope.editing.date_of_admission = doa;
		    }

		    dob = $scope.editing.demographics.date_of_birth;
		    if (dob) {
                if(!angular.isString(dob)){
                    dob = moment(dob).format(DATE_FORMAT);
                }
            }
		    $scope.editing.demographics.date_of_birth = dob;

		    $http.post('episode/', $scope.editing).success(function(episode) {
			    episode = new Episode(episode);
			    $modalInstance.close(episode);
		    });
	    };

	    $scope.cancel = function() {
		    $modalInstance.close(null);
	    };

    });
