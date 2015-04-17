angular.module('opal.services')
    .factory('recordLoader', function($q, $http, $rootScope, $window){
        var deferred = $q.defer();
        $http.get('/api/v0.1/record/').then(function(response){
            var fields = response.data;
            $rootScope.fields = fields;
            deferred.resolve(fields)
        }, function(){ $window.alert('Records could not be loaded')}
                                           );
        return deferred.promise;
});
