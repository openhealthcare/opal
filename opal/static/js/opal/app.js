var app = angular.module('opal', [
	 'opal.filters',
	 'opal.services',
	 'opal.directives',
	 'opal.controllers',
	 '$strap.directives'
]);

// See http://stackoverflow.com/questions/8302928/angularjs-with-django-conflicting-template-tags
app.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
});

app.config(function($routeProvider) {
	$routeProvider.
		when('/', {
			controller: 'EpisodeListCtrl',
			resolve: {
				schema: function(listSchemaLoader) {
					return listSchemaLoader;
				},
				episodes: function(episodesLoader) {
					return episodesLoader();
				},
				options: function(Options) {
					return Options;
				},
			},
			templateUrl: '/templates/episode_list.html'
		}).when('/episode/:id', {
			controller: 'EpisodeDetailCtrl',
			resolve: {
				schema: function(detailSchemaLoader) {
					return detailSchemaLoader;
				},
				episode: function(episodeLoader) {
					return episodeLoader();
				},
				options: function(Options) {
					return Options;
				},
			},
			templateUrl: '/templates/episode_detail.html'
		}).when('/search', {
			controller: 'SearchCtrl',
			templateUrl: '/templates/search.html',
			resolve: {
				schema: function(listSchemaLoader) {
					return listSchemaLoader;
				},
				options: function(Options) {
					return Options;
				},
			},
        }).when('/account', {
                        controller: 'AccountCtrl',
                        templateUrl: '/accounts/templates/account_detail.html'

		}).otherwise({redirectTo: '/'});
});

app.value('$strapConfig', {
	datepicker: {
		type: 'string',
		format: 'dd/mm/yyyy',
	}
});
