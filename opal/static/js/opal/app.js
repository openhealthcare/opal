var app = OPAL.module('opal', [
    'ngRoute',
    'ngProgressLite',
	'opal.filters',
	'opal.services',
	'opal.directives',
	'opal.controllers',
    'ui.bootstrap',
]);
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
