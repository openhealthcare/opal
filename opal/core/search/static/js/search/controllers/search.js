angular.module('opal.controllers').controller(
  'SearchCtrl', function(
    $rootScope, $scope, $http, $location, $analytics,
    ngProgressLite, $q, $window, PatientSummary, Paginator
  ){
  "use strict";

  var searchUrl = "/search";
  $scope.query = {searchTerm: '', autocompleteSearchTerm: ''};
  $scope.searchColumns = ['query'];
  $scope.limit = 10;
  $scope.results = [];
  $scope.searched = false;
  $scope.paginator = new Paginator($scope.search);

  $scope.getQueryParam = function(){
    if($scope.query.searchTerm.length){
      return $scope.query.searchTerm;
    }
    return $scope.query.autocompleteSearchTerm;
  };

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
        queryBackend(queryParams).then(
            function(response){
                ngProgressLite.done();
                $scope.searched = true;
                $scope.paginator = new Paginator($scope.search, response.data);
            },
            function(){
                ngProgressLite.done();
            }
        );
    }
  };

  $scope.loadResults();

  // empty the search bar if we click through and we're not running a search
  $scope.$on('$locationChangeStart', function(event, newUrl) {
    $scope.query.searchTerm = "";
  });

  // Redirect to the patient
  // if they select from
  // the autocomplete search
  $scope.selected = function(item, model, label){
    $analytics.eventTrack(
      "AutocompleteSearch-" + item.patientId,
      {
        category: "AutocompleteSearch",
        label: item.categories
      }
    );

    $scope.query.autocompleteSearchTerm = "";
    $window.location.href = item.link;
  }

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
      params[c] = $scope.getQueryParam();
    });

    $window.location.href = searchUrl + '/#/' + "?" + $.param(params);
  };
});
