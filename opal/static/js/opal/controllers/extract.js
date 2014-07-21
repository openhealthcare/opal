angular.module('opal.controllers').controller(
    'ExtractCtrl', function($scope, $http, $window, $modal,
                            filters, options, schema){

        $scope.JSON = window.JSON;
        $scope.state =  'normal';
        $scope.filters = filters;
        $scope.columns = schema.columns;
        $scope.column_names = _.map(schema.columns, function(c){
            return c.name.underscoreToCapWords();
        });

	    for (var name in options) {
		    $scope[name + '_list'] = options[name];
	    };

        $scope.model = {
            combine    : "and",
            column     : null,
            field      : null,
            queryType  : "Equals",
            query      : null,
            lookup_list: []
        };

        $scope.criteria = [_.clone($scope.model)];

        $scope.completeCriteria =  function(){
            return _.filter($scope.criteria, function(c){
                if(c.column &&  c.field &&  c.query){
                    return true
                }
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
                    function(c){ return c.type == 'token' ||  c.type ==  'list'; }),
                function(c){ return c.name.underscoreToCapWords(); }
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

        $scope.search = function(){
            $scope.state = 'pending';
            $http.post('/search/extract/', $scope.completeCriteria()).success(
                function(results){
                    $scope.results = results;
                    $scope.state = 'normal';
                }).error(function(){
                    $scope.state = 'normal';
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
			    templateUrl: '/templates/modals/save_filter_modal.html/',
			    controller: 'SaveFilterCtrl',
			    resolve: {
				    params: function() { return $scope.filters[$index]; },
			    }
		    }).result.then(function(result){
                $scope.filters[$index] = result;
            });
        }

        $scope.save = function(){

		    modal = $modal.open({
			    templateUrl: '/templates/modals/save_filter_modal.html/',
			    controller: 'SaveFilterCtrl',
			    resolve: {
				    params: function() { return {name: null, criteria: $scope.completeCriteria()}; },
			    }
		    }).result.then(function(result){
                $scope.filters.push(result);
            });
        };

    });
