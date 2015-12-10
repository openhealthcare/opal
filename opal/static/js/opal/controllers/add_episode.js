angular.module('opal.controllers')
    .controller('AddEpisodeCtrl', function($scope, $http,
                                           $timeout, $routeParams,
                                           $modalInstance, $rootScope,
                                           Episode,
                                           options,
                                           demographics) {

      var DATE_FORMAT = 'DD/MM/YYYY';
	    $scope.currentTag    = $routeParams.tag || 'mine';
	    $scope.currentSubTag = $routeParams.subtag || 'all';

	    for (var name in options) {
		    $scope[name + '_list'] = options[name];
	    };
	    $scope.editing = {
            tagging: [{}],
		    location: {

		    },
		    demographics: demographics
	    };


	    $scope.editing.tagging[0][$scope.currentTag] = true;
	    if($scope.currentSubTag != 'all'){
		    $scope.editing.tagging[0][$scope.currentSubTag] = true;
	    }

	    $scope.save = function() {
		    var dob, doa;

		    // This is a bit mucky but will do for now
		    doa = $scope.editing.date_of_admission;
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
