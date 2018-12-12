describe('Pathway', function() {
  "use strict";
  var pathway, Pathway, $httpBackend, $rootScope;
  var FieldTranslator, pathwayScope, $window;

  var pathwayDefinition = {
    icon: undefined,
    save_url: '/pathway/add_patient/sav',
    pathway_service: 'Pathway',
    finish_button_icon: "fa fa-save",
    finish_button_text: "Save",
    steps: [
      {
        'step_controller': 'FindPatientCtrl',
        'icon': 'fa fa-user',
        'template_url': '/templates/pathway/find_patient_form.html',
        'title': 'Find Patient'
      },
      {
        'api_name': 'location',
        'step_controller': 'DefaultStep',
        'icon': 'fa fa-map-marker',
        'template_url': '/templates/pathway/blood_culture_location.html',
        'title': 'Location'
      }
    ],
    display_name: 'Add Patient'
  };

  beforeEach(function(){
    $window = jasmine.createSpyObj(["alert"]);
    module('opal.controllers', function($provide){
      $provide.service('$window', function(){ return $window});
    });
    inject(function($injector) {
      Pathway = $injector.get('Pathway');
      $httpBackend = $injector.get('$httpBackend');
      $rootScope = $injector.get('$rootScope');
      FieldTranslator = $injector.get('FieldTranslator');
    });

    pathwayScope = $rootScope.$new();
    pathwayScope.$digest();
    pathway = new Pathway(pathwayDefinition);
    _.each(pathway.steps, function(step){
      step.scope = $rootScope.$new();
    });
  });

  describe("constructor", function(){
    it('should initialise the pathway properties', function(){
      expect(pathway.save_url).toEqual("/pathway/add_patient/sav");
      expect(pathway.display_name).toEqual(pathwayDefinition.display_name);
      expect(pathway.icon).toEqual(pathwayDefinition.icon);
      expect(pathway.finish_button_text).toEqual(pathwayDefinition.finish_button_text);
      expect(pathway.finish_button_icon).toEqual(pathwayDefinition.finish_button_icon);
    });
  });

  describe('register', function(){
    it('should put scopes on the steps of that api name', function(){
      pathway.register("location", "some scope");
      expect(pathway.steps[1].scope).toEqual("some scope");
    });
  });

  describe('createSteps', function(){
    it("should create add the step controller and scopes", function(){
      expect(pathway.steps.length).toBe(2);
      expect(!!pathway.steps[0].step_controller).toBe(true);
      expect(!!pathway.steps[1].step_controller).toBe(true);
    });
  });

  describe('cancel', function(){
    it("should just resolve the form result", function(){
      var called = false;
      var args = undefined;
      var result = pathway.pathwayPromise;
      result.then(function(){
        called = true;
        args = arguments;
      });
      pathway.cancel();
      pathwayScope.$apply();
      expect(called).toBe(true);
      expect(args.length).toBe(1);
      expect(args[0]).toBe(undefined);
    });
  });

  describe('preSave', function(){
    it("should do nothing", function(){
      var editing = {};
      pathway.preSave(editing);
      expect(editing).toEqual({});
    });
  });

  describe('valid', function(){
    it("should return itself", function(){
      var editing = {};
      expect(pathway.valid(editing)).toBe(true);
    });
  });

  describe('populate editing dict', function(){
    it("should return the episode as a list of arrays of 'made copied' subrecords", function(){
      var demographics = jasmine.createSpyObj(["makeCopy"]);
      demographics.makeCopy.and.returnValue({first_name: "Wilma"});
      var treatment = jasmine.createSpyObj(["makeCopy"]);
      treatment.makeCopy.and.returnValue({drug: "aspirin"});
      $rootScope.fields = {
        demographics: {single: true},
        treatment: {single: false},
        antimicrobials: {single: false}
      };
      var episode = {demographics: [demographics], antimicrobials: [], treatment: [treatment]};
      var result = pathway.populateEditingDict(episode);
      expect(result).toEqual({
        demographics: {first_name: "Wilma"},
        antimicrobials: [],
        treatment: [{drug: "aspirin"}]
      });
      expect(demographics.makeCopy).toHaveBeenCalledWith();
      expect(treatment.makeCopy).toHaveBeenCalledWith();
    });

    it("should populate an empty dictionary if an episode isn't provided", function(){
      var result = pathway.populateEditingDict();
      expect(result).toEqual({});
    });
  });

  describe('finish', function(){
    beforeEach(function(){
      spyOn(FieldTranslator, "jsToSubrecord").and.returnValue({
        "interesting": true
      });
    });

    it("should handle the results when they're an array", function(){
      var editing = {"something": [
        {
          "interesting": true
        },
        {
          "interesting": true
        }
      ]};
      var result;
      var response = pathway.pathwayPromise;
      response.then(function(x){
        result = x;
      });
      pathway.finish(editing);
      $httpBackend.expectPOST('/pathway/add_patient/sav', editing).respond("success");
      pathwayScope.$apply();
      $httpBackend.flush();
      expect(result).toEqual('success')
    });

    it("should handle pathway save errors", function(){
      var editing = {"something": [
        {
          "interesting": true
        },
        {
          "interesting": true
        }
      ]};
      var result;
      var response = pathway.pathwayPromise;
      response.then(function(x){
        result = x;
      });
      pathway.finish(editing);
      $httpBackend.expectPOST('/pathway/add_patient/sav', editing).respond(500, 'NO');
      pathwayScope.$apply();
      $httpBackend.flush();
      expect($window.alert).toHaveBeenCalledWith("unable to save patient");
    });

    it('should call the presave on each of the steps', function(){
      var editing = {"something": [
        {
          "interesting": true
        }
      ]};
      pathway.steps[0].scope = {preSave: jasmine.createSpy()};
      var result;
      var response = pathway.pathwayPromise;
      response.then(function(x){
        result = x;
      });
      pathway.finish(editing);
      $httpBackend.expectPOST('/pathway/add_patient/sav', editing).respond("success");
      pathwayScope.$apply();
      $httpBackend.flush();
      expect(result).toEqual('success');
      expect(pathway.steps[0].scope.preSave).toHaveBeenCalledWith(editing);
    });

    it("should handle the results when they're a single item", function(){
      var editing = {"something": {
          "interesting": true
      }};
      var expected = {"something": [{
          "interesting": true
      }]};
      var result;
      var response = pathway.pathwayPromise;
      response.then(function(x){
        result = x;
      });
      pathway.finish(editing);
      $httpBackend.expectPOST('/pathway/add_patient/sav', expected).respond("success");
      pathwayScope.$apply();
      $httpBackend.flush();
      expect(result).toEqual('success');
    });

    it("should remove _client from arrays if it exists", function(){
      var editing = {something: [{
          interesting: true,
          _client: {id: 1},
      }]};
      var expected = {something: [{
          interesting: true,
      }]};
      var result;
      var response = pathway.pathwayPromise;
      response.then(function(x){
        result = x;
      });
      pathway.finish(editing);
      $httpBackend.expectPOST('/pathway/add_patient/sav', expected).respond("success");
      pathwayScope.$apply();
      $httpBackend.flush();
      expect(result).toEqual('success');
    });

    it("should remove _client from single items if they exists", function(){
      var editing = {something: {
          interesting: true,
          _client: {id: 1},
      }};
      var expected = {something: [{
          interesting: true,
      }]};
      var result;
      var response = pathway.pathwayPromise;
      response.then(function(x){
        result = x;
      });
      pathway.finish(editing);
      $httpBackend.expectPOST('/pathway/add_patient/sav', expected).respond("success");
      pathwayScope.$apply();
      $httpBackend.flush();
      expect(result).toEqual('success');
    });

    it("should call compacted", function(){
      spyOn(pathway, "compactEditing").and.callThrough();
      var editing = {something: {
          interesting: true,
      }};
      var expected = {something: [{
          interesting: true,
      }]};
      var result;
      var response = pathway.pathwayPromise;
      response.then(function(x){
        result = x;
      });
      pathway.finish(editing);
      $httpBackend.expectPOST('/pathway/add_patient/sav', expected).respond("success");
      pathwayScope.$apply();
      $httpBackend.flush();
      expect(result).toEqual('success');
      expect(pathway.compactEditing).toHaveBeenCalledWith(editing);
    });

    it("should remove nulls single items if they exists", function(){
      var editing = {something: null};
      var compacted = pathway.compactEditing(editing);
      expect(compacted).toEqual({});
    });

    it("should remove nulls arrays if they exists", function(){
      var editing = {something: [null]};
      var result;
      var response = pathway.pathwayPromise;
      response.then(function(x){
        result = x;
      });
      var compacted = pathway.compactEditing(editing);
      expect(compacted).toEqual({});
    });
  });
});
