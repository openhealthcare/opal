angular.module('opal.controllers').controller(
    'EditItemCtrl', function($scope, $cookieStore, $timeout,
                             $modalInstance, $modal, $q,
                             ngProgressLite,
                             profile, item, options, episode) {

        $scope.profile = profile;
        $scope.the_episode = episode;
        $scope.episode = episode.makeCopy();
        // Some fields should only be shown for certain categories.
        // Make that category available to the template.
        $scope.episode_category = episode.category
  	    $scope.editing = item.makeCopy();

        $scope.editingMode = function(){
            return !_.isUndefined($scope.editing.id);
        };

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
  			    $scope[name + '_list'] = _.uniq(options[name]);
  		    };
  	    };

        $scope.macros = options.macros;
        $scope.select_macro = function(item){
            return item.expanded;
        };

        // TODO - don't hardcode this
	    if (item.columnName == 'microbiology_test' || item.columnName == 'lab_test' || item.columnName == 'investigation') {
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

	    $scope.episode_category_list = ['Inpatient', 'Outpatient', 'Review'];

        $scope.delete = function(result){
            $modalInstance.close(result);
                modal = $modal.open({
                templateUrl: '/templates/modals/delete_item_confirmation.html/',
                controller: 'DeleteItemConfirmationCtrl',
                resolve: {
                item: function() {
                        return item;
                    }
                }
            });
        };

        //
        // Save the item that we're editing.
        //

      $scope.saving = false;

	    $scope.save = function(result) {
          $scope.saving = true;
          ngProgressLite.set(0);
          ngProgressLite.start();
          to_save = [item.save($scope.editing)];
          if(!angular.equals($scope.the_episode.makeCopy(), $scope.episode)){
              to_save.push($scope.the_episode.save($scope.episode));
          }
          $q.all(to_save).then(function() {
              $scope.saving = false;
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

        $scope.prepopulate = function($event) {
            $event.preventDefault();
            var data = $($event.target).data()
            _.each(_.keys(data), function(key){
                if(data[key] == 'true'){
                    data[key] = true;
                    return
                }
                if(data[key] == 'false'){
                    data[key] = false;
                    return
                }
            });
            angular.extend($scope.editing, data);
        };
    });
