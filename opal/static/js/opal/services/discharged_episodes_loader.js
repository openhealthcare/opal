angular.module('opal.services')
    .factory('dischargedEpisodesLoader',
             function($q, $window,
                      EpisodeResource, Episode,
                      listSchemaLoader) {
                 return function() {
	                 var deferred = $q.defer();
	                 listSchemaLoader.then(function(schema) {
	                     EpisodeResource.query({discharged: true}, function(resources) {
		                     var episodes = {};
		                     _.each(resources, function(resource) {
		                         episodes[resource.id] = new Episode(resource, schema);
		                     });
		                     deferred.resolve(episodes);
	                     }, function() {
		                     // handle error better
		                     $window.alert('Episodes could not be loaded');
	                     });
	                 });
	                 return deferred.promise;
                 };
             });
