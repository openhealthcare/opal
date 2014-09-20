angular.module('opal.services')
    .factory('listSchemaLoader', function($q, $http, $window, $route,
                                          Schema, $rootScope) {
        return function() {
            var deferred = $q.defer();
            var tagparams = $route.current.params;
            $http.get('/schema/list/').then(function(response) {
                var schema;
	            var listSchemaNames = response.data.list_schema;
                var fields = response.data.fields;
                $rootScope.fields = fields;
                var buildFields = function(names) {
                    return _.map(names, function(name) {
                        return fields[name];
                    })
                }
                if(tagparams.subtag){
                    if(!listSchemaNames[tagparams.tag]){
                        schema = new Schema(buildFields(listSchemaNames['default']));
                    }
                    else if(listSchemaNames[tagparams.tag][tagparams.subtag]){
                        schema =  new Schema(buildFields(listSchemaNames[tagparams.tag][tagparams.subtag]));
                    }
                    else if(listSchemaNames[tagparams.tag]['default']){
                        schema = new Schema(buildFields(listSchemaNames[tagparams.tag]['default']));
                    }else {
                        schema = new Schema(buildFields(listSchemaNames['default']))
                    }
                }else if(tagparams.tag && tagparams.tag in listSchemaNames && listSchemaNames[tagparams.tag]['default']){
                    schema = new Schema(buildFields(listSchemaNames[tagparams.tag]['default']));
                }else{
                    schema = new Schema(buildFields(listSchemaNames['default']));
                }

	            deferred.resolve(schema);
            }, function() {
	            // handle error better
	            $window.alert('List schema could not be loaded');
            });

            return deferred.promise;
        }
    });
