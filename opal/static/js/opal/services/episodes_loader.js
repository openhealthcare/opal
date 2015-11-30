angular.module('opal.services')
    .factory('episodesLoader', function($q, $window,
                                        $http,
                                        $route,
                                        EpisodeResource, Episode
                                        ) {
    return function() {
      "use strict";

	    var deferred = $q.defer();
      var params = $route.current.params;
      var target = '/episode/' + params.tag;
      if(params.subtag){
          target += '/' + params.subtag;
      }

      var getEpisodePromise = $http.get(target);

      getEpisodePromise.then(function(episodesResult){
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
