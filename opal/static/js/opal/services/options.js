angular.module('opal.services').factory('Options', function($q, $http, $window) {
    var deferred = $q.defer();
    $http.get('/api/v0.1/options/').then(function(response) {
	    deferred.resolve(response.data);
    }, function() {
	    // handle error better
	    $window.alert('Options could not be loaded');
    });
    return deferred.promise;
});
