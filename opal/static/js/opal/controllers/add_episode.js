angular.module('opal.controllers')
    .controller(
        'AddEpisodeCtrl',
        function($scope, $http,
                 $timeout, $routeParams,
                 $modalInstance, $rootScope,
                 Episode, FieldTranslater,
                 referencedata,
                 demographics,
                 tags){
            "use strict";
            var currentTags = [];

            _.extend($scope, referencedata.toLookuplists());

	        $scope.editing = {
                tagging: [{}],
    		        location: {},
                demographics: demographics
	        };

          $scope.editing.tagging = {};

          if(tags.tag){
            $scope.editing.tagging[tags.tag] = true;
          }

          if(tags.subtag){
            $scope.editing.tagging[tags.subtag] = true;
          }

	        $scope.save = function() {
            var toSave = FieldTranslater.jsToPatient($scope.editing)
            // this is not good
            toSave.tagging = [toSave.tagging];

		        $http.post('/api/v0.1/episode/', toSave).success(function(episode) {
			        episode = new Episode(episode);
			        $modalInstance.close(episode);
		        });
	        };

	        $scope.cancel = function() {
		        $modalInstance.close(null);
	        };

        });
