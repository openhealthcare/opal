//
// Service to allow the common pattern of copying an episode to a different
// categrory.
//
angular.module('opal.services')
    .factory('CopyToCategory', function($http, $q, $window, Episode){

        //
        // Main entrypoint function for service
        //
        // When given an episode and a category, we return a deferred
        // that resolves with a new episode, with all details preserved
        // apart from teams (blank) and category (CATEGORY)
        //
        var CopyToCategory = function(episode_id, category){
            var deferred = $q.defer();
            $http.post('/episode/' + episode_id + '/actions/copyto/'+category).then(
                function(response){ // Success
                    deferred.resolve(new Episode(response.data));
                },
                function(response){ // Error
                    $window.alert('Unable to create a new episode in ' + category);
                    deferred.reject()
                }
            );
            return deferred.promise;
        }

        return CopyToCategory;
    });
