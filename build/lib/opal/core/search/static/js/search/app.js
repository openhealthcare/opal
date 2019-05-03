//
// Main Opal Search Angular application
//
!(function(){
  var app = OPAL.module('opal.search', [
      'ngRoute',
      'ngProgressLite',
      'ngCookies',
      'opal.config',
      'opal.filters',
      'opal.services',
      'opal.directives',
      'opal.controllers'
  ]);

  OPAL.run(app);

  app.config(function($routeProvider){
    $routeProvider
    .when('/', {
      controller: 'SearchCtrl',
      templateUrl: '/search/templates/search.html',
    })
    .when('/extract', {
        controller: 'ExtractCtrl',
        templateUrl: '/search/templates/extract.html',
        resolve: {
            profile: function(UserProfile){ return UserProfile.load(); },
            extractSchema: function(extractSchemaLoader){ return extractSchemaLoader.load(); },
            filters: function(filtersLoader){ return filtersLoader.load(); },
            referencedata: function(Referencedata){ return Referencedata.load(); }
        }
    })
  });
})();
