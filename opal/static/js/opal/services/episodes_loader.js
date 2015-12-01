angular.module('opal.services')
    .factory('episodesLoader', function($q, $window,
                                        $http,
                                        $route,
                                        EpisodeResource, Episode,
                                        recordLoader) {
    return function() {
      "use strict";

	    var deferred = $q.defer();
      var params = $route.current.params;
      var target = '/episode/' + params.tag;
      if(params.subtag){
          target += '/' + params.subtag;
      }

      var getEpisodePromise = $http.get(target);

      $q.all([recordLoader, getEpisodePromise]).then(function(results){
          // record loader updates the global scope
          // TODO look at whether it should be doing this...
          var episodesResult = results[1];
          var episodes = {};
          _.each(episodesResult.data, function(resource) {
              episodes[resource.id] = new Episode(resource);
          });
          deferred.resolve(episodes);
      }, function() {
           // handle error better
           $window.alert('Episodes could not be loaded');
     });

	    return deferred.promise;
    };
});
