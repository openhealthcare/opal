angular.module('opal.services')
    .factory('extractSchemaLoader', function($q, $http, $window, Schema){
    var deferred = $q.defer();
    $http.get('/api/v0.1/extract-schema/').then(function(response) {
	    var columns = response.data;
	    deferred.resolve(new Schema(columns));
    }, function() {
	    // handle error better
	    $window.alert('Extract schema could not be loaded');
    });

    return deferred.promise;
});
