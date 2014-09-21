angular.module('opal.services')
    .factory('UserProfile', function($q, $http, $window, $routeParams) {

        UserProfile = function(profiledata){
            var profile = this;

            angular.extend(profile, profiledata);
            
            this.active_roles = function(){
                var roles = [];
                if(this.roles['default']){
                    angular.extend(roles, this.roles['default']);
                }
                if($routeParams.tag && this.roles[$routeParams.tag]){
                    angular.extend(roles, this.roles[$routeParams.tag]);
                }
                return roles;o
            };

            this.has_role = function(role){
                return this.active_roles().indexOf(role) != -1;
            }
        };

        var deferred = $q.defer();
        $http.get('/userprofile/').then(function(response) {
	        deferred.resolve(new UserProfile(response.data) );
        }, function() {
	        // handle error better
	        $window.alert('UserProfile could not be loaded');
        });
        return deferred.promise;
    });
