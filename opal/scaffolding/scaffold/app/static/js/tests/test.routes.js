//
// Unittests for the application router
//

describe('Routes', function() {
  "use strict";

  var $route;

  beforeEach(function(){

    module('opal');

    inject(function($injector){
      $route = $injector.get('$route');
    })
  });

  describe('/', function() {

    it('should direct to the welcome controller', function() {
      var controller = $route.routes['/'].controller;
      expect('WelcomeCtrl').toEqual(controller);
    });

    it('should use the welcome template', function() {
      var controller = $route.routes['/'].templateUrl;
      expect('/templates/welcome.html').toEqual(controller);
    });

  });

});
