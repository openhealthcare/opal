angular.module('opal.controllers').controller(
    'SearchCtrl', function($scope, $http, $location, $modal,
                                              $q, Episode,
                                              schema, options) {
	$scope.searchTerms = {
		hospital_number: '',
		name: ''
	};
	$scope.results = [];
	$scope.searched = false;

	$scope.episode_category_list = ['OPAT', 'Inpatient', 'Outpatient', 'Review'];
	$scope.hospital_list = ['Heart Hospital', 'NHNN', 'UCH'];

	// $timeout(function() {
	// 	dialog.modalEl.find('input,textarea').first().focus();
	// });

	$scope.search = function() {
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


	$scope.addEpisode = function() {
		var hospitalNumberModal;

		$scope.state = 'modal';

		hospitalNumberModal = $modal.open({
			templateUrl: '/templates/modals/hospital_number.html/',
			controller: 'HospitalNumberCtrl',
            resolve: {
                schema: function(){ return schema },
                options: function(){ return options },
                tags: function(){ return {tag: 'mine', subtag: 'all'}}}
		}).result.then(
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
