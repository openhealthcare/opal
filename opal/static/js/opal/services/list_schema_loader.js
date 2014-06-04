angular.module('opal.services')
    .factory('listSchemaLoader', function($q, $http, $window, $route,
                                              Schema) {
    return function() {
    var deferred = $q.defer();
    var tagparams = $route.current.params;
    $http.get('/schema/list/').then(function(response) {
        var schema;
	    var schemas = response.data;
        if(tagparams.subtag){
            if(!schemas[tagparams.tag]){
                schema = new Schema(schemas.default);
            }
            else if(schemas[tagparams.tag][tagparams.subtag]){
                schema =  new Schema(schemas[tagparams.tag][tagparams.subtag]);
            }
        }
        if(schemas[tagparams.tag]){
            schema = new Schema(schemas[tagparams.tag].default);
        }else{
            schema = new Schema(schemas.default);
        }

	    deferred.resolve(schema);
    }, function() {
	    // handle error better
	    $window.alert('List schema could not be loaded');
    });

    return deferred.promise;
        }
});
