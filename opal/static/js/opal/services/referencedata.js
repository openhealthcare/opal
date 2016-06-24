angular.module('opal.services').factory('Referencedata', function($q, $http, $window) {
    "use strict";

    var deferred = $q.defer();
    var url = '/api/v0.1/referencedata/';

    var Referencedata = function(data){
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
        deferred.resolve(new Referencedata(response.data));
    }, function() {
	    // handle error better
	    $window.alert('Referencedata could not be loaded');
    });

    return deferred.promise;
});
