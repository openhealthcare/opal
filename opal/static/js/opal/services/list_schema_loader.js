angular.module('opal.services')
    .factory('listSchemaLoader', function($q, $http, $window, $route,
                                          Schema, 
                                          $rootScope, 
                                          recordLoader) {
        return function() {
            var deferred = $q.defer();
            var tagparams = $route.current.params;
            var schema;
            recordLoader.then(function(records){
                var fields = $rootScope.fields;

                $http.get('/api/v0.1/list-schema/').then(function(response) {
	                var listSchemaNames = response.data;

                    var buildFields = function(names) {
                        return _.map(names, function(name) {
                            return records[name];
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

            });

            return deferred.promise;
        }
    });
