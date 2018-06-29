angular.module('opal.services')
    .factory('filtersLoader', function($q, $window, FilterResource, Filter) {
    var load = function(){
        var deferred =  $q.defer();
        FilterResource.query(function(resources){
            var filters = _.map(resources, function(resource){
                return new Filter(resource);
            });
            deferred.resolve(filters)
        }, function(){
            $window.alert('Filters could not be loaded')
        });
        return deferred.promise
    }
    return {load: load};
});
