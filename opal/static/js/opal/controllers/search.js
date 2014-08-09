angular.module('opal.controllers').controller(
    'SearchCtrl', function($scope, $http, $location, $modal,
                           $timeout, ngProgressLite,
                           $q, Episode, Flow,
                           profile,
                           schema, options) {

        $scope.profile = profile;
	    $scope.searchTerms = {
		    hospital_number: '',
		    name: ''
	    };
	    $scope.results = [];
	    $scope.searched = false;

	    $scope.episode_category_list = ['OPAT', 'Inpatient', 'Outpatient', 'Review'];
	    $scope.hospital_list = ['Heart Hospital', 'NHNN', 'UCH'];

	    $timeout(function() {
		    $('#searchByName').focus();
	    });

	    $scope.search = function() {
        ngProgressLite.set(0);
        ngProgressLite.start();
		    var queryParams = [];
		    var queryString;

		    for (var term in $scope.searchTerms) {
			    if ($scope.searchTerms[term] != '') {
				    queryParams.push(term + '=' + $scope.searchTerms[term]);
			    };
		    };

		    if (queryParams.length == 0) {
			    return;
		    };

		    queryString = queryParams.join('&');

		    $http.get('patient/?' + queryString).success(function(results) {
          ngProgressLite.done();
			    $scope.searched = true;
			    $scope.results = results;
		    });
	    };

        $scope.getEpisodeID = function(patient){
            var epid = patient.active_episode_id;
            if(!epid){
                epid = _.first(_.keys(patient.episodes));
            }
            return epid;
        }

        $scope.jumpToEpisode = function(patient){
            window.open('#/episode/'+$scope.getEpisodeID(patient), '_blank');
        }

	    $scope.addEpisode = function() {
            if(profile.readonly){ return null; };

            var enter = Flow(
                'enter', schema, options, 
                {
                    current_tags: {
                        tag: 'mine',
                        subtag: 'all'
                    },
                    hospital_number: $scope.searchTerms.hospital_number
                }
            );

		    $scope.state = 'modal';

            enter.then(
                function(episode) {
			        // User has either retrieved an existing episode or created a new one,
			        // or has cancelled the process at some point.
			        //
			        // This ensures that the relevant episode is added to the table and
			        // selected.
			        $scope.state = 'normal';
			        if (episode) {
                        window.location.href = '#/episode/' + episode.id;
			        };
		        },
                function(reason){
                    $scope.state = 'normal';
                }
            );
	    };

    });
