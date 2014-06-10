angular.module('opal.services')
    .factory('UserProfile', function($q, $http, $window) {
    var deferred = $q.defer();
    $http.get('/userprofile/').then(function(response) {
	    deferred.resolve(response.data);
    }, function() {
	    // handle error better
	    $window.alert('UserProfile could not be loaded');
    });
    return deferred.promise;
});
