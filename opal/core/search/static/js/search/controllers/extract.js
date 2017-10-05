angular.module('opal.controllers').controller( 'ExtractCtrl',
  function(
    $scope, $http, $window, $modal, $timeout, $location, $anchorScroll,
    PatientSummary, Paginator, referencedata, ngProgressLite, profile, filters,
    extractSchema, dataDictionary, ExtractQuery
  ){
    "use strict";

    $scope.profile = profile;
    $scope.limit = 10;
    $scope.JSON = window.JSON;
    $scope.filters = filters;
    $scope.extractSchema = extractSchema;
    $scope.dataDictionary = dataDictionary;
    // used by the download extract
    // a slice is a cut of data, a field that we want to download
    $scope.selectSliceSubrecord = function(sliceSubrecord){
      $scope.sliceSubrecord = sliceSubrecord;
    }
    $scope.setFieldInfo = function(field){
      $scope.fieldInfo = field
    }

    $scope.searched = false;
    $scope.currentPageNumber = 1;
    $scope.paginator = new Paginator($scope.search);
    $scope.state = 'query';
    $scope.referencedata = referencedata;
    $scope.selectSliceSubrecord(dataDictionary.columns[0]);
    $scope.setFieldInfo($scope.sliceSubrecord.fields[0]);

    $scope.extractQuery = new ExtractQuery(dataDictionary);

    $scope.selectedInfo = undefined;

    $scope.selectInfo = function(query){
      $scope.selectedInfo = query;
    };

    $scope.resetFilter = function(query, fieldsTypes){
      // when we change the column, reset the rest of the query
      $scope.extractQuery.resetFilter(query, fieldsTypes);
      $scope.selectInfo(query);
    };

    //
    // Determine the appropriate lookup list for this field if
    // one exists.
    //
    $scope.refresh = function(){
      $scope.async_waiting = false;
      $scope.async_ready = false;
      $scope.searched = false;
      $scope.results = [];
    };

    $scope.$watch('extractQuery.criteria', $scope.refresh, true);

    $scope.getQueryParams = function(pageNumber){
      // the query params are the complete criteria and the
      // page number without the angular hash key
      var queryParams = angular.copy($scope.extractQuery.completeCriteria());
      if(queryParams.length){
        queryParams[0].page_number = pageNumber;
      }

      // remove the angular hash key
      _.each(queryParams, function(query){
          query = _.filter(query, function(v, k){
            return k === "%%hashKey";
          });
      });

      return queryParams;
    }

    $scope.search = function(pageNumber){
        if(!pageNumber){
            pageNumber = 1;
        }

        var queryParams = $scope.getQueryParams(pageNumber);

        if(queryParams.length){
            queryParams[0].page_number = pageNumber;
            ngProgressLite.set(0);
            ngProgressLite.start();
            $http.post('/search/extract/', queryParams).success(
                function(response){

                    // if the criteria has changed after the search has been
                    // send, don't update the search results, just discard them
                    var currentQueryParams = $scope.getQueryParams(pageNumber);
                    if(JSON.stringify(queryParams) !== JSON.stringify(currentQueryParams)){
                      return
                    }

                    $scope.results = _.map(response.object_list, function(o){
                        return new PatientSummary(o);
                    });
                    $scope.searched = true;
                    $scope.paginator = new Paginator($scope.search, response);
                    ngProgressLite.done();
                }).error(function(e){
                    ngProgressLite.set(0);
                    $window.alert('ERROR: Could not process this search. Please report it to the OPAL team');
                });
        }
        else{
          $scope.searched = true;
        }
    };

    $scope.async_extract = function(usingDataSlice){
        if($scope.async_ready){
            $window.open('/search/extract/download/' + $scope.extract_id, '_blank');
            return null;
        }
        if($scope.async_waiting){
            return null;
        }

        var ping_until_success = function(){
            if(!$scope.extract_id){
                $timeout(ping_until_success, 1000);
                return;
            }
            $http.get('/search/extract/status/'+ $scope.extract_id).then(function(result){
                if(result.data.state == 'FAILURE'){
                    $window.alert('FAILURE');
                    $scope.async_waiting = false;
                    return;
                }
                if(result.data.state == 'SUCCESS'){
                    $scope.async_ready = true;
                }else{
                    if($scope.async_waiting){
                        $timeout(ping_until_success, 1000);
                    }
                }
            });
        };
        $scope.async_waiting = true;
        var postArgs = {criteria: JSON.stringify($scope.extractQuery.criteria)};
        if(usingDataSlice){
          postArgs['data_slice'] = JSON.stringify(
            $scope.extractQuery.getDataSlices()
          );
        }
        $http.post(
            '/search/extract/download',
            postArgs
        ).then(function(result){
            $scope.extract_id = result.data.extract_id;
            ping_until_success();
        });
    };

    $scope.jumpToFilter = function($event, filter){
        $event.preventDefault();
        $scope.extractQuery.criteria = filter.criteria;
    };

    $scope.editFilter = function($event, filter, $index){
      $event.preventDefault();
      var modal = $modal.open({
        templateUrl: '/search/templates/modals/save_filter_modal.html/',
        controller: 'SaveFilterCtrl',
        resolve: {
          params: function() { return $scope.filters[$index]; }
        }
      }).result.then(function(result){
        $scope.filters[$index] = result;
      });
    };

    $scope.save = function(){
      $modal.open({
        templateUrl: '/search/templates/modals/save_filter_modal.html/',
        controller: 'SaveFilterCtrl',
        resolve: {
          params: function() { return {name: null, criteria: $scope.extractQuery.completeCriteria()}; }
        }
      }).result.then(function(result){
        $scope.filters.push(result);
      });
    };
});
