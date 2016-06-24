angular.module('opal.services')
    .factory('EpisodeDetailMixin', function($rootScope, $modal, $location, $cookieStore, Item){
        return function($scope){

            var episode = $scope.episode;
            var profile = $scope.profile;
            var options = $scope.options;
            // var schema  = $scope.schema;
            var Flow    = $scope.Flow

	        $scope.dischargeEpisode = function() {
                if(profile.readonly){ return null; };

		        $rootScope.state = 'modal';
                var exit = Flow(
                    'exit',
                    null,  // Schema ? Not used ? Todo: investigate!
                    options,
                    {
                        current_tags: {
                            tag   : $scope.currentTag,
                            subtag: $scope.currentSubTag
                        },
                        episode: $scope.episode
                    }
                );

                exit.then(function(result) {
			        $rootScope.state = 'normal';
		        });
	        };

            $scope.addEpisode = function(){
                if(profile.readonly){ return null; };

                var enter = Flow(
                    'enter', options,
                    {
                        current_tags: { tag: 'mine', subtag: '' },
                        hospital_number: $scope.episode.demographics[0].hospital_number
                    }
                );

		        $rootScope.state = 'modal';

                enter.then(
                    function(episode) {
		                // User has either retrieved an existing episode or created a new one,
		                // or has cancelled the process at some point.
		                //
		                // This ensures that the relevant episode is added to the table and
		                // selected.
		                $rootScope.state = 'normal';
                        if(episode){
                            $location.path('/episode/' + episode.id);
                        }
	                },
                    function(reason){
                        // The modal has been dismissed. We just need to re-set in order
                        // to re-enable keybard listeners.
                        $rootScope.state = 'normal';
                    });
            },


            $scope.jumpToTag = function(tag){
                $location.path(options.tag_slugs[tag]);
            };

        }
    });
