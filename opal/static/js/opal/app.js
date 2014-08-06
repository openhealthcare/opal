var app = angular.module('opal', [
    'ngRoute',
    'ngProgressLite',
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

app.run(['$rootScope', 'ngProgressLite', function($rootScope, ngProgressLite) {
  // When route started to change.
  $rootScope.$on('$routeChangeStart', function() {
      ngProgressLite.set(0);
      ngProgressLite.start();
  });

  // When route successfully changed.
  $rootScope.$on('$routeChangeSuccess', function() {
      ngProgressLite.done();
  });

  // When some error occured.
  $rootScope.$on('$routeChangeError', function() {
      ngProgressLite.set(0);
  });
}]);
