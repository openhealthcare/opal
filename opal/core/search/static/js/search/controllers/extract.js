angular.module('opal.controllers').controller(
  'ExtractCtrl',
  function(
    $scope, $http, $window, $modal, $timeout, PatientSummary, Paginator,
    referencedata, ngProgressLite, profile, filters, extractSchema
  ){
    "use strict";

    $scope.profile = profile;
    $scope.limit = 10;
    $scope.JSON = window.JSON;
    $scope.filters = filters;
    $scope.columns = extractSchema.getAdvancedSearchColumns();
    $scope.searched = false;
    $scope.currentPageNumber = 1;
    $scope.paginator = new Paginator($scope.search);

    var NOT_ADVANCED_SEARCHABLE = [
        "created", "updated", "created_by_id", "updated_by_id"
    ];
    _.extend($scope, referencedata.toLookuplists());

    $scope.combinations = ["all", "any"];
    $scope.anyOrAll = $scope.combinations[0];

    $scope.model = {
        column     : null,
        field      : null,
        queryType  : null,
        query      : null
    };

    $scope.criteria = [_.clone($scope.model)];

    $scope.readableQuery = function(someQuery){
      if(!someQuery){
        return someQuery;
      }
      var result = someQuery;
      if(someQuery === "Equals"){
        result = "is";
      }
      if(someQuery === "Before" || someQuery === "After"){
        result = "is " + result;
      }

      return result.toLowerCase();
    };

    $scope.completeCriteria =  function(){
      var combine;


      // queries can look at either all of the options, or any of them
      // ie 'and' conjunctions or 'or'
      if($scope.anyOrAll === 'all'){
        combine = "and";
      }
      else{
        combine = 'or';
      }

      // remove incomplete criteria
      var criteria = _.filter($scope.criteria, function(c){
          // Teams are a special case - they are essentially boolean
          if(c.column == 'tagging' && c.field){
              return true;
          }
          // Ensure we have a query otherwise
          var queryPopulated = true;
          if(_.isUndefined(c.query) || _.isNull(c.query)){
            queryPopulated = false;
          }
          if(c.column &&  c.field && queryPopulated){
              return true;
          }
          c.combine = combine;
          // If not, we ignore this clause
          return false;
      });

      _.each(criteria, function(c){
        c.combine = combine;
      });

      return criteria;
    };

    $scope.searchableFields = function(columnName){
        var column = $scope.findColumn(columnName);
        // TODO - don't hard-code this
        if(column){
          return _.map(
              _.reject(
                  column.fields,
                  function(c){
                      if(_.contains(NOT_ADVANCED_SEARCHABLE, c.name)){
                          return true;
                      }
                      return c.type == 'token' ||  c.type ==  'list';
                  }),
              function(c){ return c; }
          ).sort();
        }
    };

    $scope.findColumn = function(columnName){
      if(!columnName){
        return;
      }
      return _.findWhere($scope.columns, {name: columnName});
    };

    $scope.findField = function(columnName, fieldName){
      /*
      * returns the field object from the extractSchema when given column.name and field.name
      */
      var column = $scope.findColumn(columnName);
      if(!column){return;}
      return _.findWhere(
          column.fields, {name: fieldName}
      );
    };

    $scope.isType = function(column, field, type){
        var theField = $scope.findField(column, field);
        if(!column || !field){
            return false;
        }
        if(!theField){ return false; }
        if (_.isArray(type)){
            var match = false;
            _.each(type, function(t){ if(t == theField.type){ match = true; } });
            return match;
        }else{
            return theField.type == type;
        }
    };

    $scope.selectedInfo = undefined;

    $scope.selectInfo = function(query){
      $scope.selectedInfo = query;
    };

    $scope.getChoices = function(column, field){
      var modelField = $scope.findField(column, field);

      if(modelField.lookup_list && modelField.lookup_list.length){
        return $scope[modelField.lookup_list + "_list"];
      }

      if(modelField.enum){
        return modelField.enum;
      }
    };

    $scope.isBoolean = function(column, field){
        return $scope.isType(column, field, ["boolean", "null_boolean"]);
    };

    $scope.isText = function(column, field){
        return $scope.isType(column, field, "string") || $scope.isType(column, field, "text");
    };

    $scope.isSelect = function(column, field){
        return $scope.isType(column, field, "many_to_many");
    };

    $scope.isDate = function(column, field){
        return $scope.isType(column, field, "date");
    };

    $scope.isDateTime = function(column, field){
        return $scope.isType(column, field, "date_time");
    };

    $scope.isDateType = function(column, field){
        // if the field is a date or a date time
        return $scope.isDate(column, field) || $scope.isDateTime(column, field);
    };

    $scope.isNumber = function(column, field){
        return $scope.isType(column, field, ["float", "big_integer", "integer", "positive_integer_field", "decimal"]);
    };

    $scope.addFilter = function(){
        $scope.criteria.push(_.clone($scope.model));
    };

    $scope.removeFilter = function(index){
        if($scope.selectedInfo === $scope.criteria[index]){
          $scope.selectedInfo = undefined;
        }
        if($scope.criteria.length == 1){
            $scope.removeCriteria();
        }
        else{
            $scope.criteria.splice(index, 1);
        }
    };

    $scope.resetFilter = function(query, fieldsTypes){
      // when we change the column, reset the rest of the query
      _.each(query, function(v, k){
        if(!_.contains(fieldsTypes, k) && k in $scope.model){
          query[k] = $scope.model[k];
        }
      });
      if(query.column && query.field){
        $scope.selectInfo(query);
      }
      else{
        if($scope.selectedInfo && !$scope.selectedInfo.field){
          $scope.selectInfo(undefined);
        }
      }
    };

    $scope.removeCriteria = function(){
        $scope.criteria = [_.clone($scope.model)];
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

    $scope.$watch('criteria', $scope.refresh, true);

    $scope.search = function(pageNumber){
        if(!pageNumber){
            pageNumber = 1;
        }

        var queryParams = $scope.completeCriteria();

        if(queryParams.length){
            queryParams[0].page_number = pageNumber;
            ngProgressLite.set(0);
            ngProgressLite.start();
            $http.post('/search/extract/', queryParams).success(
                function(response){
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

    $scope.async_extract = function(){
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
            $http.get('/search/extract/result/'+ $scope.extract_id).then(function(result){
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
        $http.post(
            '/search/extract/download',
            {criteria: JSON.stringify($scope.criteria)}
        ).then(function(result){
            $scope.extract_id = result.data.extract_id;
            ping_until_success();
        });
    };

    $scope.jumpToFilter = function($event, filter){
        $event.preventDefault();
        $scope.criteria = filter.criteria;
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
          params: function() { return {name: null, criteria: $scope.completeCriteria()}; }
        }
      }).result.then(function(result){
        $scope.filters.push(result);
      });
    };
});
