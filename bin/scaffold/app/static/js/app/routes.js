var app = angular.module('opal');
app.config(
    ['$routeProvider',
     function($routeProvider){
	     $routeProvider.when('/',  {redirectTo: '/list'})
     }]);

