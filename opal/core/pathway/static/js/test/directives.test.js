describe('pathway directives', function(){
  "use strict";

  var element, scope, $httpBackend, $compile, $rootScope, mockModal, $parse;
  var referencedata, metadata, pathwayLoader;
  beforeEach(module('opal.controllers'));
  beforeEach(module('opal.directives', function($provide){
    mockModal = {open: function(){}};
    spyOn(mockModal, "open").and.returnValue({
      result: {
        then: function(fn){
          fn({episode_id: 1, patient_id: 1, redirect_url: "somewhere"});
        }
      }
    });

    $provide.service('episodeLoader', function(){});
    $provide.service('$modal', function(){ return mockModal});
    referencedata = {
      load: function(){
        return {
          then: function(fn){ fn({ toLookuplists: function(){ return {}; } }); }
        }
      }
    }
    $provide.service('Referencedata', function(){
      return referencedata;
    });

    metadata = {
      load: function(){
        return {
          then: function(fn){ fn({ toLookuplists: function(){ return {}; } }); }
        };
      }
    };

    $provide.service('Metadata', function(){
      return metadata;
    });
  }));

  beforeEach(inject(function($injector){
    var $rootScope = $injector.get('$rootScope');
    scope = $rootScope.$new();
    $httpBackend = $injector.get('$httpBackend');
    $compile = $injector.get('$compile');
    $parse = $injector.get('$parse');
    pathwayLoader = $injector.get('pathwayLoader');
  }));

  describe('openPathway', function(){
    describe('open the modal', function(){
      it('should trigger the call to open the modal', function(){
        scope.callback = jasmine.createSpy().and.returnValue("something");
        pathwayLoader = jasmine.createSpyObj(["load"]);
        pathwayLoader.load.and.returnValue("pathway result");
        var markup = '<a href="#" open-pathway="someSpy" pathway-callback="callback"></a>';
        element = $compile(markup)(scope);
        scope.$digest();
        $(element).click();
        scope.$digest();
        expect(mockModal.open).toHaveBeenCalled();
        var modalCallArgs = mockModal.open.calls.argsFor(0)[0];
        expect(modalCallArgs.resolve.pathwayCallback()()()).toEqual("something");
      });

      it('should load the pathway when the modal is opened with the episode', function(){
        scope.callback = jasmine.createSpy().and.returnValue("something");
        var episode = {demographics: [{patient_id: 2}], id: 1};
        scope.episode = episode;
        pathwayLoader = jasmine.createSpyObj(["load"]);
        pathwayLoader.load.and.returnValue("pathway result");
        var markup = '<a href="#" pathway-episode="episode" open-pathway="someSpy" pathway-callback="callback"></a>';
        element = $compile(markup)(scope);
        scope.$digest();
        $(element).click();
        scope.$digest();
        expect(mockModal.open).toHaveBeenCalled();
        var modalCallArgs = mockModal.open.calls.argsFor(0)[0];
        expect(modalCallArgs.resolve.pathwayDefinition(pathwayLoader)).toEqual("pathway result");
        expect(pathwayLoader.load).toHaveBeenCalledWith("someSpy", 2, 1);
      });

      it('should pass through the pathway name when the modal is opened', function(){
        pathwayLoader = jasmine.createSpyObj(["load"]);
        pathwayLoader.load.and.returnValue("pathway result");
        var markup = '<a href="#" open-pathway="someFakePathway"></a>';
        element = $compile(markup)(scope);
        scope.$digest();
        $(element).click();
        scope.$digest();
        expect(mockModal.open).toHaveBeenCalled();
        var modalCallArgs = mockModal.open.calls.argsFor(0)[0];
        expect(modalCallArgs.resolve.pathwayName()).toEqual("someFakePathway");
      });
    })

    it('should work without a call back', function(){
      var markup = '<a href="#" open-pathway="someSpy"></a>';
      spyOn(referencedata, "load").and.returnValue("referencedata");
      spyOn(metadata, "load").and.returnValue("metadata");
      spyOn(pathwayLoader, "load")
      element = $compile(markup)(scope);
      scope.$digest();
      $(element).click();
      scope.$digest();
      expect(mockModal.open).toHaveBeenCalled();

      var modalCallArgs = mockModal.open.calls.argsFor(0)[0];
      expect(modalCallArgs.resolve.metadata()).toBe("metadata");
      expect(metadata.load).toHaveBeenCalled();
      expect(modalCallArgs.resolve.referencedata()).toBe("referencedata");
      expect(referencedata.load).toHaveBeenCalled();
      expect(modalCallArgs.resolve.pathwayCallback()()).toEqual(scope.callback);

      modalCallArgs.resolve.pathwayDefinition(pathwayLoader);
      expect(pathwayLoader.load).toHaveBeenCalledWith("someSpy");
    });

    it('should wrap the call back in a function', function(){
      scope.callback = jasmine.createSpy();
      spyOn(_, "partial");
      var markup = '<a href="#" open-pathway="someSpy" pathway-callback="callback"></a>';
      element = $compile(markup)(scope);
      scope.$digest();
      $(element).click();
      scope.$digest();
      expect(_.partial).toHaveBeenCalledWith($parse("callback"), _, scope);
    });

    it('should take the episode off pathway-episode parameter', function(){
      scope.callback = jasmine.createSpy();
      scope.onions = "trees";
      spyOn(_, "partial");
      var markup = '<a href="#" pathway-episode="onions" open-pathway="someSpy" pathway-callback="callback"></a>';
      element = $compile(markup)(scope);
      scope.$digest();
      $(element).click();
      scope.$digest();
      var resolves = mockModal.open.calls.mostRecent().args[0].resolve;
      expect(resolves.episode()).toBe('trees');
    });
  });

  describe('requiredIfNotEmpty', function(){
    var markup = '<form name="form"><input name="something_model" ng-model="editing.something.interesting" required-if-not-empty="editing.something"></form>';
    it('should not be an error if none of the model is populated', function(){
        scope.editing = {something: {}};
        element = $compile(markup)(scope);
        var form = angular.element(element.find("input")[0]).scope().form;
        scope.$digest();
        expect(form.$error).toEqual({});
    });

    it('should be an error if some of the scope is filled in', function(){
      scope.editing = {something: {}};
      scope.editing.something.blah = "hello";
      element = $compile(markup)(scope);
      var form = angular.element(element.find("input")[0]).scope().form;
      scope.$digest();
      expect(form.something_model.$error.requiredIfNotEmpty).toBe(true);
    });

    it('should not be an error if te required field is populated', function(){
      scope.editing = {something: {interesting: "hello"}};
      element = $compile(markup)(scope);
      var form = angular.element(element.find("input")[0]).scope().form;
      scope.$digest();
      expect(form.$error).toEqual({});
    });

    it('should stop being an error if subsequently a field is populated', function(){
      scope.editing = {something: {}};
      element = $compile(markup)(scope);
      var form = angular.element(element.find("input")[0]).scope().form;
      scope.$digest();
      expect(form.$error).toEqual({});
      scope.editing.something.else = "there";
      scope.$digest();
      expect(form.something_model.$error.requiredIfNotEmpty).toBe(true);
    });
  });

  describe("pathwayLink", function(){
    it("should set the href on the element", function(){
      scope.someEpisode = {
        id: 10,
        demographics: [{patient_id: 2}]
      };
      var markup = '<a href="#" pathway-episode="someEpisode" pathway-link="somePathway"></a>';
      element = $compile(markup)(scope);
      scope.$digest();
      expect(element.attr("href")).toEqual("/pathway/#/somePathway/2/10");
    });
  });


  describe("pathwayStep", function(){
    it("register a scope with the pathway", function(){
      var pathway = {
        steps: [{
          api_name: "someThing",
          step_controller: "DefaultStep"
        }],
        episode: "someEpisode",
        register: function(){}
      };
      spyOn(pathway, "register");
      var markup = '<div href="#" pathway-step="someThing"></div>';
      scope.pathway = pathway;
      element = $compile(markup)(scope);
      scope.someEpisode = {
        id: 10,
        demographics: [{patient_id: 2}]
      };
      scope.$digest();
      expect(pathway.register).toHaveBeenCalled();
      var stepScope = pathway.register.calls.argsFor(0);
      expect(stepScope[0]).toEqual("someThing");

      // verifying a scope is tricky, but lets make sure something
      // is passed through
      expect(!!stepScope[1]).toBe(true);
    });
  });
});
