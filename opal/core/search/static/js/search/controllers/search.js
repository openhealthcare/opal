angular.module('opal.controllers').controller(
    'SearchCtrl', function($rootScope, $scope, $http, $location, $modal,
                           $timeout, ngProgressLite,
                           $q, $window, Flow,
                           PatientSummary, Paginator) {
      "use strict";

      var searchUrl = "/search";
      var inSearch = $location.path() === searchUrl;
	    $scope.query = {searchTerm: '', autocompleteSearchTerm: ''};
      $scope.searchColumns = ['query'];
      $scope.limit = 10;
	    $scope.results = [];
	    $scope.searched = false;
	    $scope.episode_category_list = ['OPAT', 'Inpatient', 'Outpatient', 'Review'];
	    $scope.hospital_list = ['Heart Hospital', 'NHNN', 'UCH'];
      $scope.paginator = new Paginator($scope.search);

      var getQueryParam = function(){
          if($scope.query.searchTerm.length){
            return $scope.query.searchTerm;
          }
          return $scope.query.autocompleteSearchTerm;
      }

        $scope.disableShortcuts = function(){
            $rootScope.state = "search";
        };

        $scope.enableShortcuts = function(){
            $rootScope.state = "normal";
        };

        var queryBackend = function(queryParams){
          var queryString = $.param(queryParams);
          return $http.get('/search/simple/?' + queryString).success(function(response) {
            $scope.results = _.map(response.object_list, function(o){
                return new PatientSummary(o);
            });
          });
        };

        $scope.loadResults = function(){
            var queryString;
            var urlParams = $location.search();

            // this view only allows a couple a couple of search columns
            // but allow a search on either of these
            $scope.query.searchTerm = _.find(urlParams, function(v, k){
                if(_.contains($scope.searchColumns, k)){
                    return true;
                }
            }) || "";

            if($scope.query.searchTerm.length){
                ngProgressLite.set(0);
                ngProgressLite.start();
                var queryParams = $location.search();
                queryBackend(queryParams).then(function(response){
                    ngProgressLite.done();
                    $scope.searched = true;
                    $scope.paginator = new Paginator($scope.search, response.data);
                });
            }
        };

        if($location.path() === searchUrl){
            $scope.loadResults();
        }

        // empty the search bar if we click through and we're not running a search
        $scope.$on('$locationChangeStart', function(event, newUrl) {
            $scope.query.searchTerm = "";
        });

        // redirect to the patient
        // if they select from
        // the drop down list
        $scope.$on('$typeahead.select', function(event, patientSummary) {
          $window.location.href = patientSummary.link;
        });


        $scope.$watch("query.autocompleteSearchTerm", function(){
          if($scope.query.autocompleteSearchTerm.length){
            queryBackend({query: $scope.query.autocompleteSearchTerm});
          }
        });

	    $scope.search = function(pageNumber) {
            var params = {};

            if(pageNumber){
                params.page_number = pageNumber;
            }

            _.each($scope.searchColumns, function(c){
                params[c] = getQueryParam();
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

        window.scope = $scope;
    });
