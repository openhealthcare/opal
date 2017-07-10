describe('DefaultSingleStep', function(){
  "use strict";
  var scope, step, $controller, controller;

  beforeEach(function(){
    module('opal.controllers');
    inject(function($injector){
      var $rootScope = $injector.get('$rootScope');
      scope = $rootScope.$new();
      $controller = $injector.get('$controller');
    });
    scope.editing = {};

    step = {model_api_name: "demographics"};
  });

  it('if the editing exists, put the last element of this model api name onto the scope', function(){
    scope.editing = {demographics: [{first_name: "Dave"}]};
    controller = $controller('DefaultSingleStep', {
      scope: scope,
      step: step,
      episode: null
    });

    expect(scope.editing.demographics).toEqual({first_name: "Dave"});
  });

  it('if the episode exists, create a new item on the list', function(){
    var episode = jasmine.createSpyObj(["newItem"]);
    episode.newItem.and.returnValue("someData");
    controller = $controller('DefaultSingleStep', {
      scope: scope,
      step: step,
      episode: episode
    });

    expect(scope.editing.demographics).toBe("someData");
    expect(episode.newItem).toHaveBeenCalledWith("demographics");
  });

  it('if there is no episode', function(){
    controller = $controller('DefaultSingleStep', {
      scope: scope,
      step: step,
      episode: null
    });

    expect(scope.editing.demographics).toEqual({});
  });
});
