angular.module('opal.controllers').controller(
    'EditItemCtrl', function($scope, $cookieStore, $timeout,
                             $modalInstance, $modal,
                             ngProgressLite, item, options, episode) {
        $scope.episode = episode.makeCopy();
        // Some fields should only be shown for certain categories.
        // Make that category available to the template.
        $scope.episode_category = episode.location[0].category
	    $scope.editing = item.makeCopy();

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

        // 
        // Save the item that we're editing.
        // 
	    $scope.save = function(result) {
            ngProgressLite.set(0);
            ngProgressLite.start();
		    item.save($scope.editing).then(function() {
                ngProgressLite.done();
			    $modalInstance.close(result);
		    });
	    };

        // Let's have a nice way to kill the modal.
	    $scope.cancel = function() {
		    $modalInstance.close('cancel');
	    };

        $scope.undischarge = function() {
            undischargeMoadal = $modal.open({
                templateUrl: '/templates/modals/undischarge.html/',
                controller: 'UndischargeCtrl',
                resolve: {episode: function(){ return episode } }
            }
            ).result.then(function(result){
                $modalInstance.close(episode.location[0])
            });
        };
    });
