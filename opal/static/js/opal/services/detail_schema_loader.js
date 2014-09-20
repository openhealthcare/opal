angular.module('opal.services')
    .factory('detailSchemaLoader', function($q, $http, $window, $rootScope, Schema) { 
        var deferred = $q.defer();
        $http.get('/schema/detail/').then(function(response) {
            var schema;
            $rootScope.fields = response.data.fields;
            var schema = new Schema(response.data.detail_schema)
            deferred.resolve(schema)
        }, function() { // handle error better
	        $window.alert('Detail schema could not be loaded');
        });

        return deferred.promise;
    });
