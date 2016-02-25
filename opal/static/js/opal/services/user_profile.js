angular.module('opal.services')
    .factory('UserProfile', function($q, $http, $window, $routeParams) {

        var UserProfile = function(profiledata){
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
            }

            this.can_edit = function(record_name){
                // This is non-scalable.
                if(this.has_role('scientist')){
                    if(['lab_test', 'lab_specimin'].indexOf(record_name) != -1){
                        return false;
                    }
                }
                return true;
            }

        };

        var deferred = $q.defer();

        url = '/api/v0.1/userprofile/';

        $http({ cache: true, url: url, method: 'GET'}).then(function(response) {
          deferred.resolve(new UserProfile(response.data) );
        }, function() {
          // handle error better
          $window.alert('UserProfile could not be loaded');
        });

        return deferred.promise;
    });
