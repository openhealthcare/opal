angular.module('opal.controllers').controller(
    'EditItemCtrl', function($scope, $cookieStore, $timeout,
                             $modalInstance,
                             item, options, episode) {
    $scope.episode = episode.makeCopy();
	$scope.editing = item.makeCopy();
    $scope.state = 'editing';

    // This is the patientname displayed in the modal header
	$scope.editingName = item.episode.demographics[0].name;

    $scope.columnName = item.columnName;
    // initially display episodes of interest to current user
    $scope.currentTag = $cookieStore.get('opal.currentTag') || 'mine';
    // initially display episodes of interest to current user
    $scope.currentSubTag = 'all';

    $scope.showSubtags = function(withsubtags){
		return _.some(withsubtags, function(tag){ return item[tag] });
    };

    // TODO - reimplement this
	$timeout(function() {
		$modalInstance.modalEl.find('input,textarea').first().focus();
	});

	for (var name in options) {
		if (name.indexOf('micro_test') != 0) {
			$scope[name + '_list'] = options[name];
		};
	};

	if (item.columnName == 'microbiology_test') {
		$scope.microbiology_test_list = [];
		$scope.microbiology_test_lookup = {};
		$scope.micro_test_defaults =  options.micro_test_defaults;

		for (var name in options) {
			if (name.indexOf('micro_test') == 0) {
				for (var ix = 0; ix < options[name].length; ix++) {
					$scope.microbiology_test_list.push(options[name][ix]);
					$scope.microbiology_test_lookup[options[name][ix]] = name;
				};
			};
		};

		$scope.$watch('editing.test', function(testName) {
			$scope.testType = $scope.microbiology_test_lookup[testName];
            if( _.isUndefined(testName) || _.isUndefined($scope.testType) ){
                return;
            }
            if($scope.testType in $scope.micro_test_defaults){
                _.each(
                    _.pairs($scope.micro_test_defaults[$scope.testType]),
                    function(values){
                        var field =  values[0];
                        var _default =  values[1];
                        var val = _default
                        if($scope.editing[field]){
                            val = $scope.editing[field]
                        }
                        $scope.editing[field] =  val;
                    });
            }
		});
	};

	$scope.episode_category_list = ['OPAT',  'Inpatient', 'Outpatient', 'Review'];

	$scope.save = function(result) {
        $scope.state = 'saving';
		item.save($scope.editing).then(function() {
            // if($scope.columnName == 'location'){
            //     episode.save($scope.episode).then(function(){
            //         $modalInstance.close(result)
            //     });
            // }else{
			    $modalInstance.close(result);
            // }
		});
	};

	$scope.cancel = function() {
		$modalInstance.close('cancel');
	};
});
