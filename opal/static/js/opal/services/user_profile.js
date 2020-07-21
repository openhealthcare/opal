angular.module('opal.services')
    .service('UserProfile', function($q, $http, $window, $routeParams) {
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

        return {
          load: load
        };
    });
