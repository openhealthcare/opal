angular.module('opal.services').factory('User', function($q, $http, $window){
    "use strict";

    var API  = '/api/v0.1/user/';

    var User = function(data){
        this.initialize(data);
    };

    User.prototype = {

        initialize: function(data){
            _.extend(this, data);
        }

    };

    //
    // Fetch all Users from the API
    //
    var all = function(){
        var deferred = $q.defer();
        $http({ cache: true, url: API, method: 'GET'}).then(
            function(response){
                var users = _.map(response.data, function(userdata){
                    return new User(userdata);
                });
                deferred.resolve(users);
            },
            function(response){
                // handle error better
                $window.alert('Users could not be loaded');
            }
        );
        return deferred.promise;
    };

    //
    // Fetch an individual User from the API by ID
    //
    var get = function(id){
        var deferred = $q.defer();
        var url = API + id + '/';
        $http({ cache: true, url: url, method: 'GET'}).then(
            function(response){
                deferred.resolve(new User(response.data));
            },
            function(response){
                // handle error better
                $window.alert('User could not be loaded');
            }
        );
        return deferred.promise;
    }

    return {
        all: all,
        get: get
    }

});
