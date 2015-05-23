angular.module('opal.controllers')
    .controller('AddEpisodeCtrl', function($scope, $http,
                                           $timeout, $routeParams,
                                           $modalInstance, $rootScope,
                                           Episode, schema,
                                           options,
                                           demographics) {

	    $scope.currentTag    = $routeParams.tag || 'mine';
	    $scope.currentSubTag = $routeParams.subtag || 'all';

	    for (var name in options) {
		    $scope[name + '_list'] = options[name];
	    };
        
        // TODO: deprecate these
	    $scope.episode_category_list = ['OPAT', 'Inpatient', 'Outpatient', 'Review'];
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
		    var value;

		    // This is a bit mucky but will do for now
		    value = $scope.editing.date_of_admission;
		    if (value) {
                if(typeof value == 'string'){
                    var doa = moment(value, 'DD/MM/YYYY').format('YYYY-MM-DD');
                }else{
                    var doa = moment(value).format('YYYY-MM-DD');
                }
			    $scope.editing.date_of_admission = doa;
		    }

		    value = $scope.editing.demographics.date_of_birth;
		    if (value) {
                if(typeof value == 'string'){
                    var dob = moment(value, 'DD/MM/YYYY').format('YYYY-MM-DD');
                }else{
                    var dob = moment(value).format('YYYY-MM-DD');
                }
			    $scope.editing.demographics.date_of_birth = dob;
		    }

		    $http.post('episode/', $scope.editing).success(function(episode) {
			    episode = new Episode(episode);
			    $modalInstance.close(episode);
		    });
	    };

	    $scope.cancel = function() {
		    $modalInstance.close(null);
	    };

    });
