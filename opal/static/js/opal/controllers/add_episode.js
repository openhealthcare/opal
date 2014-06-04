angular.module('opal.controllers')
    .controller('AddEpisodeCtrl', function($scope, $http, $cookieStore,
                                           $timeout,
                                           $modalInstance, Episode, schema,
                                           options,
                                           demographics) {
	$scope.currentTag = $cookieStore.get('opal.currentTag') || 'mine';
	$scope.currentSubTag = $cookieStore.get('opal.currentSubTag') || 'all';

    // TODO - find a way to reimplement this
	// $timeout(function() {
	// 	dialog.modalEl.find('input,textarea').first().focus();
	// });

	for (var name in options) {
		$scope[name + '_list'] = options[name];
	};

	$scope.episode_category_list = ['OPAT', 'Inpatient', 'Outpatient', 'Review'];

    // TODO - this is no longer the way location/admission date works.
	$scope.editing = {
		date_of_admission: moment().format('DD/MM/YYYY'),
        tagging: {},
		location: {
            hospital: 'UCLH'
		},
		demographics: demographics
	};
	$scope.editing.tagging[$scope.currentTag] = true;
	if($scope.currentSubTag != 'all'){
		$scope.editing.tagging[$scope.currentSubTag] = true;
	}

	$scope.showSubtags = function(withsubtags){
		var show =  _.some(withsubtags, function(tag){
            return $scope.editing.tagging[tag]
        });
		return show
	};

	$scope.save = function() {
		var value;

		// This is a bit mucky but will do for now
        // TODO - this is obviously broken now that location is not like this.
		value = $scope.editing.date_of_admission;
		if (value) {
            var doa = moment(value, 'DD/MM/YYYY').format('YYYY-MM-DD');
			$scope.editing.date_of_admission = doa;
		}

		value = $scope.editing.demographics.date_of_birth;
		if (value) {
            var dob = moment(value, 'DD/MM/YYYY').format('YYYY-MM-DD');
			$scope.editing.demographics.date_of_birth = dob;
		}

		$http.post('episode/', $scope.editing).success(function(episode) {
			episode = new Episode(episode, schema);
			$modalInstance.close(episode);
		});
	};

	$scope.cancel = function() {
		$modalInstance.close(null);
	};
});
