describe('DefaultStep', function(){
  "use strict";
  var $controller, $rootScope, scope;

  beforeEach(function(){
    module('opal.controllers');
    inject(function($injector){
      $controller = $injector.get('$controller');
      $rootScope = $injector.get('$rootScope');
    });
    scope = $rootScope.$new();
    scope.editing = {};
    scope.editing.helper = jasmine.createSpyObj(['addRecord']);
  });

  it('should add an empty instance if we have a model name', function(){
    var controller = $controller('DefaultStep', {
      scope: scope,
      step: {model_api_name: "something"},
      episode: {}
    });
    expect(scope.editing.helper.addRecord).toHaveBeenCalledWith('something');

  });

  it("should not add an empty instance if we don't have a model name", function(){
    var controller = $controller('DefaultStep', {
      scope: scope,
      step: {},
      episode: {}
    });
    expect(scope.editing.helper.addRecord).not.toHaveBeenCalled();
  });

  it("should not add an instance if we already have an instance", function(){
    scope.editing["something"] = [{some: "subrecord"}];
    var controller = $controller('DefaultStep', {
      scope: scope,
      step: {model_api_name: "something"},
      episode: {model_api_name: "something"}
    });
    expect(scope.editing.helper.addRecord).not.toHaveBeenCalled();
  });

});
