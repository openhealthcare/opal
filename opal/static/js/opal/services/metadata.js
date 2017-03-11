angular.module('opal.services').factory('Metadata', function($q, $http, $window, $log) {
    "use strict";

    var url = '/api/v0.1/metadata/';

    var Metadata = function(data){
        var self = this;

        self.get = function(what){
            return self[what];
        }

        self.initialize = function(){
            _.extend(self, data)
        }

        self.initialize();
        return self;
    };

    var load = function(){
      var deferred = $q.defer();
      $http({ cache: true, url: url, method: 'GET'}).then(function(response) {
          deferred.resolve(new Metadata(response.data));
      }, function() {
        // handle error better
        $window.alert('Metadata could not be loaded');
      });

      return deferred.promise;
    };

    return {
      load: load,
      then: function(fn){
        // TODO: 0.9.0
        $log.error("This API is being deprecated and will be removed in 0.9.0. Please use Metadata.load()");
        load().then(function(result){ fn(result); });
      }
    };
});
