angular.module('opal.services')
    .factory('detailSchemaLoader', function($q, $http, $window, Schema) {
    var deferred = $q.defer();
    $http.get('/schema/detail/').then(function(response) {
        deferred.resolve(new Schema(response.data))
    }, function() {
	    // handle error better
	    $window.alert('Detail schema could not be loaded');
    });

    return deferred.promise;
});
