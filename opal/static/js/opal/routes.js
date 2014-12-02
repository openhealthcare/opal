var app = angular.module('opal')
app.config(
    ['$routeProvider',
     function($routeProvider) {
	     $routeProvider.when('/',  {redirectTo: '/list'})

             .when('/list/:tag?/:subtag?', {
			     controller: 'EpisodeListCtrl',
			     resolve: {
				     schema: function(listSchemaLoader) { return listSchemaLoader(); },
				     episodes: function(episodesLoader) { return episodesLoader(); },
				     options: function(Options) { return Options; },
                     profile: function(UserProfile){ return UserProfile },
                     viewDischarged: function(){ return false },
                     episodeVisibility: function(episodeVisibility){
                         return episodeVisibility
                     }
			     },
			     templateUrl: function(params){
                     var target =  '/templates/episode_list.html';
                     if(params.tag){
                         target += '/' + params.tag;
                         if(params.subtag){
                             target += '/' + params.subtag;
                         }
                     }
                     return target
                 }
		     })

             .when('/episode/:id', {
			     controller: 'EpisodeDetailCtrl',
			     resolve: {
				     schema: function(detailSchemaLoader) { return detailSchemaLoader; },
				     episode: function(episodeLoader) { return episodeLoader(); },
				     options: function(Options) { return Options; },
                     profile: function(UserProfile){ return UserProfile }
			     },
			     templateUrl: '/templates/episode_detail.html'
		     })
             .when('/search', {
			     controller: 'SearchCtrl',
			     templateUrl: '/templates/search.html',
			     resolve: {
                     profile: function(UserProfile){ return UserProfile },
				     schema: function(listSchemaLoader) { return listSchemaLoader(); },
				     options: function(Options) { return Options; }
			     }
             })
             .when('/discharge/:tag?/:subtag?', {
                 controller: 'EpisodeListCtrl',
                 resolve   : {
                     schema: function(listSchemaLoader){ return listSchemaLoader() },
                     options: function(Options){ return Options },
                     episodes: function(dischargedEpisodesLoader){
                         return dischargedEpisodesLoader()
                     },
                     episodeVisibility: function(episodeVisibility){
                         return episodeVisibility
                     },
                     profile: function(UserProfile){ return UserProfile },
                     viewDischarged: function(){ return true }
                 },

			     templateUrl: function(params){
                     var target =  '/templates/discharge_list.html';
                     if(params.tag){
                         target += '/' + params.tag;
                         if(params.subtag){
                             target += '/' + params.subtag;
                         }
                     }
                     return target
                 }
             })
             .when('/extract', {
                 controller: 'ExtractCtrl',
                 templateUrl: '/templates/extract.html',
                 resolve: {
                     profile: function(UserProfile){ return UserProfile },
                     schema: function(extractSchemaLoader){ return extractSchemaLoader },
				     options: function(Options) { return Options; },
                     filters: function(filtersLoader){ return filtersLoader() }
                 }
             })
             .when('/account', {
                 controller: 'AccountCtrl',
                 templateUrl: '/accounts/templates/account_detail.html'

		     })
             .otherwise({redirectTo: '/'});
     }])
