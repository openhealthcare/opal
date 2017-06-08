angular.module('opal.controllers').controller(
    'EditItemCtrl', function($scope, $timeout,
                             $modalInstance, $modal, $q,
                             ngProgressLite, $analytics,
                             referencedata, metadata,
                             profile, item, episode) {
            $scope.profile = profile;
            $scope.the_episode = episode;
            $scope.episode = episode.makeCopy();
            // Some fields should only be shown for certain categories.
            // Make that category available to the template.
            $scope.episode_category = episode.category;
            $scope.editing = {};
            $scope.item = item;
            $scope.editing[item.columnName] = item.makeCopy();
            $scope.metadata = metadata

            $scope.editingMode = function(){
                return !_.isUndefined($scope.editing[item.columnName].id);
            };

            $analytics.eventTrack(item.columnName, {
              category: "EditItem", label: episode.category_name
            });

            // This is the patient name displayed in the modal header
            $scope.editingName = episode.getFullName();

            $scope.columnName = item.columnName;
            _.extend($scope, referencedata.toLookuplists());

            $scope.macros = metadata.macros;
            $scope.select_macro = function(item){
                return item.expanded;
            };

            // TODO - don't hardcode this
            if (item.columnName == 'microbiology_test' || item.columnName == 'lab_test' || item.columnName == 'investigation') {
                $scope.microbiology_test_list = [];
                $scope.microbiology_test_lookup = {};
                $scope.micro_test_defaults =  metadata.micro_test_defaults;

                for (var name in referencedata){
                    if (name.indexOf('micro_test') == 0) {
                        for (var ix = 0; ix < referencedata[name].length; ix++) {
                            $scope.microbiology_test_list.push(referencedata[name][ix]);
                            $scope.microbiology_test_lookup[referencedata[name][ix]] = name;
                        };
                    };
                };
            var watchName= "editing." + item.columnName + ".test"
                $scope.$watch(watchName, function(testName, oldValue) {
                    $scope.testType = $scope.microbiology_test_lookup[testName];
              if(oldValue == testName){
                return;
              }

              _.each(_.keys($scope.editing[item.columnName]), function(field){
                  if(field !== "test" && field !== "_client" && field !== "date_ordered" && field !== "alert_investigation"  && field !== "id" && field !== "episode_id" && field !== "consistency_token"){
                      $scope.editing[item.columnName][field] = undefined;
                  }
              });

              if( _.isUndefined(testName) || _.isUndefined($scope.testType) ){
                  return;
              }

              if($scope.testType in $scope.micro_test_defaults){
                  _.each(_.pairs($scope.micro_test_defaults[$scope.testType]), function(values){
                      var field =  values[0];
                      var val =  values[1];
                      if(!$scope.editing[item.columnName][field]){
                          $scope.editing[item.columnName][field] = val;
                      }
                  });
              }
                });
            };

            $scope.delete = function(result){
                $modalInstance.close(result);
                var modal = $modal.open({
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

            $scope.preSave = function(editing){};

	        $scope.save = function(result) {
                ngProgressLite.set(0);
                ngProgressLite.start();
                $scope.preSave($scope.editing);
                to_save = [item.save($scope.editing[item.columnName])];
                if(!angular.equals($scope.the_episode.makeCopy(), $scope.episode)){
                    to_save.push($scope.the_episode.save($scope.episode));
                }

                $q.all(to_save).then(function() {
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
                angular.extend($scope.editing[item.columnName], data);
            };

    });
