angular.module('opal.controllers').controller(
    'SearchCtrl', function($rootScope, $scope, $http, $location, $modal,
                           $timeout, ngProgressLite,
                           $q, $window, Flow,
                           PatientSummary, Paginator) {

        var searchUrl = "/search";
	    $scope.searchTerm = '';
        $scope.searchColumns = ['query'];
        $scope.limit = 10;
	    $scope.results = [];
	    $scope.searched = false;
	    $scope.episode_category_list = ['OPAT', 'Inpatient', 'Outpatient', 'Review'];
	    $scope.hospital_list = ['Heart Hospital', 'NHNN', 'UCH'];
        $scope.paginator = new Paginator($scope.search);

        $scope.disableShortcuts = function(){
            $rootScope.state = "search";
        };

        $scope.enableShortcuts = function(){
            $rootScope.state = "normal";
        };

        $scope.loadResults = function(){
            var queryString;
            var urlParams = $location.search();

            // this view only allows a couple a couple of search columns
            // but allow a search on either of these
            $scope.searchTerm = _.find(urlParams, function(v, k){
                if(_.contains($scope.searchColumns, k)){
                    return true;
                }
            }) || "";

            if($scope.searchTerm.length){
                ngProgressLite.set(0);
                ngProgressLite.start();

                queryString = $.param($location.search());
                $http.get('/search/simple/?' + queryString).success(function(response) {
                    ngProgressLite.done();
          			$scope.searched = true;
                    $scope.results = _.map(response.object_list, function(o){
                        return new PatientSummary(o);
                    });
                    $scope.paginator = new Paginator($scope.search, response);
    		    });
            }
        };

        if($location.path() === searchUrl){
            $scope.loadResults();
        }

        // empty the search bar if we click through and we're not running a search
        $scope.$on('$locationChangeStart', function(event, newUrl) {
            $scope.searchTerm = "";
        });

	    $scope.search = function(pageNumber) {
            var params = {};

            if(pageNumber){
                params.page_number = pageNumber;
            }

            _.each($scope.searchColumns, function(c){
                params[c] = $scope.searchTerm;
            });

            if($window.location.pathname !== "/"){
                $window.location.href="/#" + searchUrl + "?" + $.param(params);
            }
            else{
                $location.url(searchUrl);
                $location.search(params);
            }
	    };

        $scope.getEpisodeID = function(patient){
            var epid = patient.active_episode_id;
            if(!epid){
                epid = _.first(_.keys(patient.episodes));
            }
            return epid;
        };

        $scope.jumpToEpisode = function(patient){
            $location.path('/episode/'+$scope.getEpisodeID(patient));
        };
    });
