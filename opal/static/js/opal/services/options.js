angular.module('opal.services').factory('Options', function($q, $http, $window) {
    var deferred = $q.defer();
    var url = '/api/v0.1/options/';
    $http({ cache: true, url: url, method: 'GET'}).then(function(response) {
      deferred.resolve(response.data);
    }, function() {
	    // handle error better
	    $window.alert('Options could not be loaded');
    });

    return deferred.promise;
});
