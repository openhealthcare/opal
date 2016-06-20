angular.module('opal.services').factory('Metadata', function($q, $http, $window) {
    "use strict";

    var deferred = $q.defer();
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


    $http({ cache: true, url: url, method: 'GET'}).then(function(response) {
        deferred.resolve(new Metadata(response.data));
    }, function() {
	    // handle error better
	    $window.alert('Metadata could not be loaded');
    });

    return deferred.promise;
});
