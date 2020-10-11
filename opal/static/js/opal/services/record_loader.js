angular.module('opal.services')
    .factory('recordLoader', function($q, $http, $rootScope, $window){
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

  return {
    load: load
  };
});
