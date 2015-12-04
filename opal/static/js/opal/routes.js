var app = angular.module('opal');

app.config(
    ['$routeProvider',
     function($routeProvider) {
             $routeProvider.when('/list/',{
                controller: 'EpisodeRedirectListCtrl',
                templateUrl: '/templates/episode_list.html',
                resolve: {
                    options: function(Options){ return Options; }
                }
             }).when('/list/:tag/:subtag?', {
			     controller: 'EpisodeListCtrl',
			     resolve: {
				     schema: function(listSchemaLoader) { return listSchemaLoader(); },
				     episodes: function(episodesLoader) { return episodesLoader(); },
				     options: function(Options) { return Options; },
                     profile: function(UserProfile){ return UserProfile; },
                     episodeVisibility: function(episodeVisibility){
                         return episodeVisibility;
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
                     return target;
                 }
		     })
             .when('/patient/:id', {
			     controller: 'PatientDetailCtrl',
                 resolve: {
				     episodes: function(patientLoader) { return patientLoader(); },
				     options: function(Options) { return Options; },
                     profile: function(UserProfile){ return UserProfile; }
                 },
			     templateUrl: function(params){ return '/templates/patient_notes.html' }
             })
             .when('/episode/:id', {
			     controller: 'EpisodeDetailCtrl',
			     resolve: {
				     episode: function(episodeLoader) { return episodeLoader(); },
				     options: function(Options) { return Options; },
                     profile: function(UserProfile){ return UserProfile; }
			     },
			     templateUrl: function(params){ return '/templates/episode_detail.html/' + params.id; }
		     })
             .when('/search', {
			     controller: 'SearchCtrl',
			     templateUrl: '/search/templates/search.html',
             })
             .when('/extract', {
                 controller: 'ExtractCtrl',
                 templateUrl: '/search/templates/extract.html',
                 resolve: {
                     profile: function(UserProfile){ return UserProfile; },
                     schema: function(extractSchemaLoader){ return extractSchemaLoader; },
				     options: function(Options) { return Options; },
                     filters: function(filtersLoader){ return filtersLoader(); }
                 }
             })
             .when('/account', {
                 controller: 'AccountCtrl',
                 templateUrl: '/accounts/templates/account_detail.html'
		     })
             .otherwise({redirectTo: '/'});
     }]);
