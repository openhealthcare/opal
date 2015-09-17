angular.module('opal.services')
    .factory('patientLoader', function($q, $window, $http, $route, Episode ) {
    return function() {
	    var deferred = $q.defer();
        var hospitalNumber = $route.current.params.id;

        if(!hospitalNumber){
            deferred.resolve([])
        }

        target = "/patient/" + hospitalNumber;

        $http.get(target).then(
            function(resources) {
                var episodes = _.map(resources.data, function(resource) {
                    return new Episode(resource);
                });
                deferred.resolve(episodes);
            }, function() {
                // handle error better
                $window.alert('Episodes could not be loaded');
            });

	    return deferred.promise;
    };
});
