describe('PathwayRedirectCtrl', function(){
  "use strict";
  var scope, step, $controller, mockWindow;

  beforeEach(function(){
    module('opal.controllers');
    mockWindow = {location: {href: null}};
    inject(function($injector){
      $controller = $injector.get('$controller');
    });
  });

  it('should redirect', function(){
    $controller('PathwayRedirectCtrl', {$window: mockWindow});
    expect(mockWindow.location.href).toBe("/");
  });
});
