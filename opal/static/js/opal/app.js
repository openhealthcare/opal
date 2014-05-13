var app = angular.module('opal', [
    'ngRoute',
	'opal.filters',
	'opal.services',
	'opal.directives',
	'opal.controllers',
    'ui.bootstrap',
]);

// See http://stackoverflow.com/questions/8302928/angularjs-with-django-conflicting-template-tags
app.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
});

app.config(
    ['$routeProvider',
     function($routeProvider) {
	     $routeProvider.when('/',  {redirectTo: '/list'})

             .when('/list/:tag?/:subtag?', {
			     controller: 'EpisodeListCtrl',
			     resolve: {
				     schema: function(listSchemaLoader) { return listSchemaLoader; },
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
				     schema: function(listSchemaLoader) { return listSchemaLoader; },
				     options: function(Options) { return Options; }
			     }
             })
             .when('/discharge', {
                 controller: 'EpisodeListCtrl',
                 templateUrl  : '/templates/discharge_list.html',
                 resolve   : {
                     schema: function(listSchemaLoader){ return listSchemaLoader },
                     options: function(Options){ return Options },
                     episodes: function(dischargedEpisodesLoader){
                         return dischargedEpisodesLoader()
                     },
                     episodeVisibility: function(episodeVisibility){
                         return episodeVisibility
                     },
                     profile: function(UserProfile){ return UserProfile },
                     viewDischarged: function(){ return true }
                 }
             })
             .when('/extract', {
                 controller: 'ExtractCtrl',
                 templateUrl: '/templates/extract.html',
                 resolve: {
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

app.value('$strapConfig', {
	datepicker: {
		type: 'string',
		format: 'dd/mm/yyyy'
	}
});
