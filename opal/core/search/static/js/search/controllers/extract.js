angular.module('opal.controllers').controller(
    'ExtractCtrl', function($scope, $http, $window, $modal, PatientSummary,
                            ngProgressLite, profile, filters, options, schema){

        var underscoreToCapWords = function(str) {
            return str.toLowerCase().replace(/_/g, ' ').replace(
                    /(?:\b)(\w)/g, function(s, p){ return p.toUpperCase(); });
        };

        $scope.profile = profile;
        $scope.limit = 10;
        $scope.JSON = window.JSON;
        $scope.filters = filters;
        $scope.columns = schema.getAdvancedSearchColumns();
        $scope.searched = false;
        $scope.currentPageNumber = 1;
        NOT_ADVANCED_SEARCHABLE = [
          "created", "updated", "created_by_id", "updated_by_id"
        ]

	    for (var name in options) {
		    $scope[name + '_list'] = options[name];
	    };

        $scope.model = {
            combine    : "and",
            column     : null,
            field      : null,
            queryType  : null,
            query      : null,
            lookup_list: []
        };

        $scope.criteria = [_.clone($scope.model)];

        $scope.completeCriteria =  function(){
            return _.filter($scope.criteria, function(c){
                // Teams are a special case - they are essentially boolean
                if(c.column == 'tagging' && c.field){
                    return true
                }
                // Ensure we have a query otherwise
                if(c.column &&  c.field &&  c.query){
                    return true
                }
                // If not, we ignore this clause
                return false
            })
        };

        $scope.searchableFields = function(column){
            // TODO - don't hard-code this
            if(column.name == 'microbiology_test'){
                return [
                    'Test',
                    'Date Ordered',
                    'Details',
                    'Microscopy',
                    'Organism',
                    'Sensitive Antibiotics',
                    'Resistant Antibiotics'
                ]
            }
            return _.map(
                _.reject(
                    column.fields,
                    function(c){
                      if(_.contains(c.name, NOT_ADVANCED_SEARCHABLE)){
                        return false;
                      }
                      return c.type == 'token' ||  c.type ==  'list';
                    }),
                function(c){ return underscoreToCapWords(c.name); }
            );
        };

        $scope.isType = function(column, field, type){
            if(!column || !field){
                return false;
            }
            var col = _.find($scope.columns, function(item){return item.name == column.toLowerCase().replace( / /g,  '_')});
            var theField =  _.find(col.fields, function(f){return f.name == field.toLowerCase().replace( / /g,  '_')});
            if(!theField){ return false }
            return theField.type == type;
        };

        $scope.isBoolean = function(column, field){
            return $scope.isType(column, field, "boolean");
        };

        $scope.isText = function(column, field){
            return $scope.isType(column, field, "string") || $scope.isType(column, field, "text");
        }

        $scope.isDate = function(column, field){
            return $scope.isType(column, field, "date");
        };

        $scope.addFilter = function(){
            $scope.criteria.push(_.clone($scope.model));
        };

        $scope.removeFilter = function(index){
            $scope.criteria.splice(index, 1);
        };

        $scope.resetFilter = function(index, dontReset){
            for (k in $scope.model) {
                if (dontReset.indexOf(k) == -1) {
                    $scope.criteria[index][k] = $scope.model[k];
                }
            }
        };

        $scope.removeCriteria = function(){
            $scope.searched = false;
            $scope.criteria = [_.clone($scope.model)];
        };

        //
        // Determine the appropriate lookup list for this field if
        // one exists.
        //
        $scope.$watch('criteria', function(){
            _.map($scope.criteria, function(c){
                var column = _.findWhere($scope.columns, {name: c.column});
                if(!column){return}
                if(!c.field){return}
                var field = _.findWhere(column.fields, {name: c.field.toLowerCase().replace(/ /g, '_')});
                if(!field){return}
                if(field.lookup_list){
                    c.lookup_list = $scope[field.lookup_list + '_list'];
                }
            });
        }, true);

        $scope.search = function(pageNumber){
            if(!pageNumber){
                pageNumber = 1;
            }

            var queryParams = $scope.completeCriteria();

            if(queryParams.length){
                queryParams[0].page_number = pageNumber;
            }
            ngProgressLite.set(0);
            ngProgressLite.start();
            $http.post('/search/extract/', queryParams).success(
                function(response){
                    $scope.results = _.map(response.object_list, function(o){
                        return new PatientSummary(o);
                    });
                    $scope.searched = true;
                    $scope.currentPageNumber = response.page_number;
                    $scope.totalPages = _.range(1, response.total_pages + 1);
                    $scope.totalCount = response.total_count;
                    ngProgressLite.done();
                }).error(function(e){
                    ngProgressLite.set(0);
                    $window.alert('ERROR: Could not process this search. Please report it to the OPAL team')
                });
        };

        $scope.jumpToFilter = function($event, filter){
            $event.preventDefault()
            $scope.criteria = filter.criteria;
        }

        $scope.editFilter = function($event, filter, $index){
            $event.preventDefault();
		    modal = $modal.open({
			    templateUrl: '/search/templates/modals/save_filter_modal.html/',
			    controller: 'SaveFilterCtrl',
			    resolve: {
				    params: function() { return $scope.filters[$index]; }
			    }
		    }).result.then(function(result){
                $scope.filters[$index] = result;
            });
        }

        $scope.save = function(){

		    modal = $modal.open({
			    templateUrl: '/search/templates/modals/save_filter_modal.html/',
			    controller: 'SaveFilterCtrl',
			    resolve: {
				    params: function() { return {name: null, criteria: $scope.completeCriteria()}; }
			    }
		    }).result.then(function(result){
                $scope.filters.push(result);
            });
        };

        $scope.jumpToEpisode = function(episode){
            window.open('#/episode/'+episode.id, '_blank');
        }

    });
