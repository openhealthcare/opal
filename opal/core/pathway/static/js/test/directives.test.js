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
    $rootScope    = $injector.get('$rootScope');
    scope         = $rootScope.$new();
    $httpBackend  = $injector.get('$httpBackend');
    $compile      = $injector.get('$compile');
    $parse        = $injector.get('$parse');
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

    it('should set up the state variable', function() {
      var markup = '<a href="#" open-pathway="someFakePathway"></a>';
      mockModal.open.and.returnValue({result: {then:function(cb, eb){
        // Conspicuously not calling cb();
      }}})
      element = $compile(markup)(scope);
      $(element).click();
      expect($rootScope.state).toEqual('modal');
    });

    it('should reset the state variable', function() {
      var markup = '<a href="#" open-pathway="someFakePathway"></a>';
      element = $compile(markup)(scope);
      scope.$digest();
      $(element).click();
      scope.$digest();
      expect($rootScope.state).toEqual('normal');
    });

    it('should reset the state variable in case of rejection', function() {
      var markup = '<a href="#" open-pathway="someFakePathway"></a>';
      mockModal.open.and.returnValue({result: {then:function(cb, eb){
        eb() // Conspicuously calling the rejection case
      }}})
      element = $compile(markup)(scope);
      $(element).click();
      scope.$digest();
      expect($rootScope.state).toEqual('normal');
    });

  });


  describe('saveMultipleWrapper template get', function(){
    it('should render its template', function(){
      var markup = '<div save-multiple-wrapper="editing.diagnosis"></div>';
      $httpBackend.expectGET('/templates/pathway/save_multiple.html').respond("");
      element = $compile(markup)(scope);
      scope.$digest();
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

  describe("initialisation of multisave", function(){
    it('should create an array on the parent scope with an empty object with an _client if none exists', function(){
      scope.editing = {greeting: undefined};
      var markup = '<div save-multiple-wrapper="editing.greeting"><div id="holla" ng-repeat="editing in model.subrecords">[[ editing.salutation ]]</div></div>';
      element = $compile(markup)(scope);
      scope.$digest();
      expect(scope.editing.greeting[0]._client.completed).toBe(false);
      expect(scope.editing.greeting[0]._client.id.indexOf("greeting")).toBe(0);
    });

    it('should not override completed if already set', function(){
      scope.editing = {greeting: {salutation: "hello", _client: {completed: false}}};
      var markup = '<div save-multiple-wrapper="editing.greeting"><div id="holla" ng-repeat="editing in model.subrecords">[[ editing.salutation ]]</div></div>';
      element = $compile(markup)(scope);
      scope.$digest();
      expect(scope.editing.greeting).toEqual([{salutation: "hello", _client: {completed: false}}]);
    });


    it('should create an array on the parent scope if given an object', function(){
      scope.editing = {greeting: {salutation: "hello"}};
      var markup = '<div save-multiple-wrapper="editing.greeting"><div id="holla" ng-repeat="editing in model.subrecords">[[ editing.salutation ]]</div></div>';
      element = $compile(markup)(scope);
      scope.$digest();
      expect(scope.editing.greeting).toEqual([{salutation: "hello", _client: {completed: true}}]);
    });
  })

  describe('multiple save wrapper scope changes', function(){
    var innerScope;

    beforeEach(function(){
      scope.editing = {greetings: [
        {salutation: "Hello!"},
        {salutation: "Hola!"}
      ]};
      var markup = '<div save-multiple-wrapper="editing.greetings"><div id="greeting" ng-repeat="editing in model.subrecords">[[ editing.salutation ]]</div></div>';
      element = $compile(markup)(scope);
      scope.$digest();
      var input = angular.element($(element).find("#greeting")[0]);
      innerScope = input.scope();
    });

    it('should populate child scope', function(){
        expect(_.isFunction(innerScope.addAnother)).toBe(true);
        expect(_.isFunction(innerScope.remove)).toBe(true);
        expect(_.isFunction(innerScope.recordFilledIn)).toBe(true);
        expect(_.isFunction(innerScope.edit)).toBe(true);
        expect(_.isFunction(innerScope.done)).toBe(true);
        expect(innerScope.model.subrecords[0].greetings.salutation).toBe("Hello!");
        expect(innerScope.model.subrecords[0].greetings._client.completed).toBe(true);
        expect(innerScope.model.subrecords[1].greetings.salutation).toBe("Hola!");
        expect(innerScope.model.subrecords[1].greetings._client.completed).toBe(true);
    });

    it('should add an empty model if there are currently no models', function(){
      scope.editing = {greetings: []};
      var markup = '<div save-multiple-wrapper="editing.greetings"><div id="greeting" ng-repeat="editing in model.subrecords">[[ editing.salutation ]]</div></div>';
      element = $compile(markup)(scope);
      scope.$digest();
      var input = angular.element($(element).find("#greeting")[0]);
      innerScope = input.scope();
      expect(!!innerScope.model.subrecords[0].greetings).toBe(true);
    });

    it('should change the child scope when something is added to the parent scope', function(){
      scope.editing.greetings.push({salutation: "Kon'nichiwa!"});
      scope.$digest();
      expect(innerScope.model.subrecords[0].greetings.salutation).toBe("Hello!");
      expect(innerScope.model.subrecords[1].greetings.salutation).toBe("Hola!");
      expect(innerScope.model.subrecords[2].greetings.salutation).toBe("Kon'nichiwa!");
    });

    it('should change the child scope when something is removed from the parent scope', function(){
      scope.editing.greetings.splice(1, 1);
      scope.$digest();
      expect(innerScope.model.subrecords.length).toBe(1);
      expect(innerScope.model.subrecords[0].greetings.salutation).toBe("Hello!");
    });

    it('should change the child scope when something is changed on the parent scope', function(){
      scope.editing.greetings[0].salutation = "Kon'nichiwa!";
      scope.$digest();
      expect(innerScope.model.subrecords.length).toBe(2);
      expect(innerScope.model.subrecords[0].greetings.salutation).toBe("Kon'nichiwa!");
    });

    it("should change the parent scope when something is added to the child scope", function(){
      innerScope.model.subrecords.push({greetings: {salutation: "Kon'nichiwa!"}});
      scope.$digest();
      expect(scope.editing.greetings.length).toBe(3);
      expect(scope.editing.greetings[2].salutation).toBe("Kon'nichiwa!");
    });

    it("should change the parent scpoe when something is removed to the child scope", function(){
      innerScope.model.subrecords.splice(1, 1);
      scope.$digest();
      expect(scope.editing.greetings.length).toBe(1);
      expect(scope.editing.greetings[0].salutation).toBe("Hello!");
    });

    it("should change the parent scope when something is removed to the child scope", function(){
      innerScope.model.subrecords.splice(1, 1);
      scope.$digest();
      expect(scope.editing.greetings.length).toBe(1);
      expect(scope.editing.greetings[0].salutation).toBe("Hello!");
    });

    it("add another should add a new object when we click add another", function(){
      innerScope.addAnother();
      scope.$digest();
      expect(scope.editing.greetings.length).toBe(3);
      expect(scope.editing.greetings[2]._client.completed).toBe(false);
      expect(scope.editing.greetings[2]._client.id.indexOf("greetings")).toBe(0);
    });

    it("should remove new objects when remove is clicked", function(){
      innerScope.remove(1);
      scope.$digest();
      expect(scope.editing.greetings[0].salutation).toBe("Hello!");
    });

    it("should tell you whether the record is filled in", function(){
      expect(!!innerScope.recordFilledIn(scope.editing.greetings[0])).toBe(true);
    });

    it("should tell you if the record has not been filled in", function(){
      var someRecord = {
        $someAngluarVar: "as",
        _client: {completed: false}
      }
      expect(!!innerScope.recordFilledIn(someRecord)).toBe(false);
    });

    it("should ignore empty strings when telling you if a record has been filled in", function(){
      var someRecord = {
        someVar: "",
        _client: {completed: false}
      }
      expect(!!innerScope.recordFilledIn(someRecord)).toBe(false);
    });

    it("done should mark a subrecord as completed", function(){
      var someRecord = {
        $someAngluarVar: "as",
        _client: {completed: false},
        someVar: true
      }
      innerScope.done(someRecord);
      expect(someRecord._client.completed).toBe(true);
    });

    it("done should populate _client if it doesn't exist", function(){
      var someRecord = {
        $someAngluarVar: "as",
        someVar: true
      }
      innerScope.done(someRecord);
      expect(someRecord._client.completed).toBe(true);
    });

    it("edit should mark a subrecord as not completed", function(){
      var someRecord = {
        $someAngluarVar: "as",
        _client: {completed: true},
        someVar: true
      }
      innerScope.edit(someRecord);
      expect(someRecord._client.completed).toBe(false);
    });

    it("edit should create _client if it doesn't exist", function(){
      var someRecord = {
        $someAngluarVar: "as",
        someVar: true
      }
      innerScope.edit(someRecord);
      expect(someRecord._client.completed).toBe(false);
    });

    it("should see changes made to additional objects on the inner objects should reflect externally", function(){
      innerScope.addAnother();
      scope.$digest();
      innerScope.model.subrecords[2].greetings.salutation = "Kon'nichiwa!";
      scope.$digest();
      expect(scope.editing.greetings[2].salutation).toBe("Kon'nichiwa!");
      expect(scope.editing.greetings[2]._client.completed).toBe(false);
    });

    it("should see changes made to additional objects on the inner objects should reflect externally", function(){
      scope.editing.greetings.push({salutation: "Kon'nichiwa!"});
      scope.$digest();
      scope.editing.greetings[2].salutation = "Ciao";
      scope.$digest();
      expect(scope.editing.greetings[2].salutation).toBe("Ciao");
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
