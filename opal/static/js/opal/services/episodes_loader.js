angular.module('opal.services')
    .factory('episodesLoader', function($q, $window,
                                        $http,
                                        $route,
                                        EpisodeResource, Episode,
                                        listSchemaLoader) {
    return function() {
      "use strict";

	    var deferred = $q.defer();
      var params = $route.current.params;
      var listSchemaPromise = listSchemaLoader();
      var target = '/episode/' + params.tag;
      if(params.subtag){
          target += '/' + params.subtag;
      }

      var getEpisodePromise = $http.get(target);

      $q.all([listSchemaPromise, getEpisodePromise]).then(function(results){
          var listSchema = results[0];
          var episodesResult = results[1];
          var episodes = {};
          _.each(episodesResult.data, function(resource) {
              episodes[resource.id] = new Episode(resource, listSchema);
          });
          deferred.resolve(episodes);
      });

	    return deferred.promise;
    };
});
