angular.module('opal.services').factory('Referencedata', function($q, $http, $window) {

    "use strict";

    var url = '/api/v0.1/referencedata/';

    var Referencedata = function(data){
        var self = this;

        var lists = _.keys(data);

        self.initialize = function(){
            _.extend(self, data)
        }

        self.get = function(what){
            return self[what];
        }

        //
        // For reasons that can only be termed 'legacy', many parts of the
        // OPAL ecosystem expect reference data to be available from lookup
        // lists with the _list suffix.
        //
        // We use this function here to move the code that generates them
        // into one place - as this logic was replicated at in least 15 places
        // at the time of writing.
        //
        self.toLookuplists = function(){
            var lookuplists = {};
            _.each(lists, function(list_name){
                lookuplists[list_name + '_list'] = self[list_name];
            });
            return lookuplists;
        };

        self.initialize();
        return self;
    };

    var load = function(){
      var deferred = $q.defer();
      $http({ cache: true, url: url, method: 'GET'}).then(function(response) {
          deferred.resolve(new Referencedata(response.data));
      }, function() {
        // handle error better
        $window.alert('Referencedata could not be loaded');
      });
      return deferred.promise;
    };

    return {
      load: load
    };
});
