angular.module('opal.controllers').controller(
    'EditItemCtrl', function($scope,
                             $modalInstance, $modal, $q,
                             ngProgressLite, $analytics,
                             referencedata, metadata,
                             profile, item, episode) {
            $scope.profile = profile;
            $scope.the_episode = episode;
            $scope.episode = episode.makeCopy();
            // Some fields should only be shown for certain categories.
            // Make that category available to the template.
            $scope.episode_category = episode.category_name;
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


            $scope.delete = function(){
                var deferred = $q.defer();
                $modalInstance.close(deferred.promise);
                var deleteModal =  $modal.open({
                    templateUrl: '/templates/delete_item_confirmation_modal.html',
                    controller: 'DeleteItemConfirmationCtrl',
                    resolve: {
                        item: function() {
                            return item;
                        }
                    }
                });
                deleteModal.result.then(function(result){
                    deferred.resolve(result)
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
                $q.all(to_save).then(
                    function() {
                        ngProgressLite.done();
      			        $modalInstance.close(result);
		            },
                    function(){
                        ngProgressLite.done();
                    }
                );
	        };

            // Let's have a nice way to kill the modal.
	        $scope.cancel = function() {
		        $modalInstance.close('cancel');
	        };

    });
