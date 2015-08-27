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
        $scope.limit = 10;
	    $scope.results = [];
	    $scope.searched = false;
        $scope.currentPageNumber = 1;

	    $scope.episode_category_list = ['OPAT', 'Inpatient', 'Outpatient', 'Review'];
	    $scope.hospital_list = ['Heart Hospital', 'NHNN', 'UCH'];

	    $timeout(function() {
		    $('#searchByName').focus();
	    });

	    $scope.search = function(pageNumber) {
            if(!pageNumber){
                pageNumber = 1;
            }
            ngProgressLite.set(0);
            ngProgressLite.start();
		    var queryParams = [];
		    var queryString;

		    for (var term in $scope.searchTerms) {
			    if ($scope.searchTerms[term] != '') {
				    queryParams.push(term + '=' + $scope.searchTerms[term]);
			    };
		    };

		    if (queryParams.length === 0) {
			    return;
		    };

            queryParams.push("page_number=" + pageNumber);
		    queryString = queryParams.join('&');

		    $http.get('/search/patient/?' + queryString).success(function(response) {
                ngProgressLite.done();
			    $scope.searched = true;
                $scope.results = response.object_list;
                $scope.currentPageNumber = response.page_number;
                $scope.totalPages = _.range(1, response.total_pages + 1);
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
            $location.path('/episode/'+$scope.getEpisodeID(patient));
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
