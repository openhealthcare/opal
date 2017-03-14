angular.module('opal.services')
    .service('UserProfile', function($q, $http, $window, $routeParams, $log) {
        var UserProfile = function(profiledata){
            var profile = this;

            angular.extend(profile, profiledata);

            this.active_roles = function(){
                var roles = [];
                if(this.roles['default']){
                    roles = angular.copy(this.roles['default']);
                }
                if($routeParams.slug && this.roles[$routeParams.slug]){
                    roles = _.union(roles, this.roles[$routeParams.slug]);
                }
                return roles;
            };

            this.has_role = function(role){
                return this.active_roles().indexOf(role) != -1;
            };

            // TODO: don't hardcode these roles
            this.can_see_pid = function(){
                if(this.has_role('researcher') || this.has_role('scientist')){
                    return false;
                }
                return true;
            };

            this.can_edit = function(record_name){
                // This is non-scalable.
                if(this.has_role('scientist')){
                    if(['lab_test', 'ridrti_test'].indexOf(record_name) == -1){
                        return false;
                    }
                }
                return true;
            };
        };

        var load = function(){
          var deferred = $q.defer();

          url = '/api/v0.1/userprofile/';

          $http({ cache: true, url: url, method: 'GET'}).then(function(response) {
            deferred.resolve(new UserProfile(response.data) );
          }, function() {
            // handle error better
            $window.alert('UserProfile could not be loaded');
          });

          return deferred.promise;
        };

        var promise = load();

        return {
          load: function(){ return promise; },
          then: function(fn){
            // TODO: 0.9.0
            $log.warn("This API is being deprecated and will be removed in 0.9.0. Please use UserProfile.load()");
            promise.then(function(result){ fn(result); });
          }
        };
    });
