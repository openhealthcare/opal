angular.module('opal.services')
    .factory('recordLoader', function($q, $http, $rootScope, $window, $log){
    "use strict";

  var load = function(){
    var deferred = $q.defer();
    var url = '/api/v0.1/record/';
    $http({ cache: true, url: url, method: 'GET'}).then(function(response){
        var fields = response.data;
        $rootScope.fields = fields;
        deferred.resolve(fields);
    }, function(){ $window.alert('Records could not be loaded');}
                                       );
    return deferred.promise;
  };

  var promise = load();

  return {
          load: function(){ return promise; },
    then: function(fn){
      // TODO: 0.9.0
      $log.warn("This API is being deprecated and will be removed in 0.9.0. Please use recordLoader.load()");
      promise.then(function(result){ fn(result); });
    }
  };
});
