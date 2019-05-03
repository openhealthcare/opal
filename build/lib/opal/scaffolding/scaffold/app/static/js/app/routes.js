(function(){
  var app = angular.module('opal');
  app.controller('WelcomeCtrl', function(){});

  app.config(
      ['$routeProvider',
       function($routeProvider){
  //	     $routeProvider.when('/',  {redirectTo: '/list'})

           $routeProvider.when('/',  {
               controller: 'WelcomeCtrl',
               templateUrl: '/templates/welcome.html'}
                              )

       }]);
})();
