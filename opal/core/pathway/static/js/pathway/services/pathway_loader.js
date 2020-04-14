angular.module('opal.services')
  .factory('pathwayLoader', function($q, $route, $http, $window){
    return {
      load: function(pathwayName, patientId, episodeId) {
      	    var deferred = $q.defer();
            url = '/pathway/detail/' + pathwayName;

            if(patientId && !episodeId){
              url = url + "/" + patientId;
            }

            if(episodeId){
              url = url + "/" + patientId + "/" + episodeId;
            }

            $http({ cache: true, url: url, method: 'GET'}).then(
              function(resource) {
      		        deferred.resolve(resource.data);
              },
              function() {
      	        // handle error better
      	        $window.alert('Pathway could not be loaded');
              }
            );
      	    return deferred.promise;
      }
    }
});
