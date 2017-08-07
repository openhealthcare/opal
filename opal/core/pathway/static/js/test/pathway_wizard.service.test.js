describe('WizardPathway', function() {
  "use strict";
  var pathway, WizardPathway, $httpBackend, PathwayScopeCompiler, $rootScope;
  var pathwayScope, $q;

  var pathwayDefinition = {
    'icon': undefined,
    'save_url': '/pathway/add_patient/sav',
    'pathway_service': 'WizardPathway',
    'steps': [
      {
        'step_controller': 'DefaultStep',
        'icon': 'fa fa-user',
        'template_url': '/templates/pathway/find_patient_form.html',
        'display_name': 'Find Patient',
        'api_name': 'find_patient'
      },
      {
        'step_controller': 'DefaultStep',
        'icon': 'fa fa-map-marker',
        'template_url': '/templates/pathway/blood_culture_location.html',
        'display_name': 'Location',
        'api_name': 'location',
      }
    ],
    'title': 'Add Patient'
  };

  beforeEach(function(){
    module('opal.services');
    module('opal.controllers');
    inject(function($injector) {
      $httpBackend = $injector.get('$httpBackend');
      $rootScope = $injector.get('$rootScope');
      WizardPathway = $injector.get('WizardPathway');
      $q = $injector.get('$q');
    });

    pathwayScope = $rootScope.$new();
    var deferred = $q.defer();
    deferred.resolve(pathwayScope);
    pathway = new WizardPathway(pathwayDefinition);
    pathwayScope.$apply();
  });

  describe("initialise", function(){
    it("should setup additional variables on initilisation", function(){
      expect(pathway.numSteps).toBe(2);
      expect(pathway.currentStep).toEqual(pathway.steps[0]);
      expect(pathway.currentScope).toEqual(pathway.steps[0].scope);
      expect(pathway.currentIndex).toBe(0);
    });
  });

  describe("hasNext", function(){
    it("it should return false if there are no more steps", function(){
      pathway.currentIndex = 1;
      expect(pathway.hasNext()).toBe(false);
    });
    it("it should return true if there are more steps", function(){
      expect(pathway.hasNext()).toBe(true);
    });
  });

  describe("hasPrevious", function(){
    it("should return true if there are previous steps", function(){
      pathway.goNext();
      expect(!!pathway.hasPrevious()).toBe(true);
    });

    it("should return false if there aren't previous steps", function(){
      expect(!!pathway.hasPrevious()).toBe(false);
    });
  });

  describe('goToStep', function(){
    it('should go to a step with that api name', function(){
      pathway.goToStep('location');
      expect(pathway.currentIndex).toBe(1);
      expect(pathway.currentStep.api_name).toBe('location');
    });
  });

  describe("goNext", function(){
    it("should move current variables to the next step", function(){
      pathway.goNext({});
      expect(pathway.currentIndex).toBe(1);
      expect(pathway.currentStep).toEqual(pathway.steps[1]);
      expect(pathway.currentScope).toEqual(pathway.steps[1].scope);
    });
  });

  describe("goPrevious", function(){
    it("should move current variables to the next step", function(){
      pathway.goNext({});
      pathway.goPrevious({});
      expect(pathway.currentIndex).toBe(0);
      expect(pathway.currentStep).toEqual(pathway.steps[0]);
      expect(pathway.currentScope).toEqual(pathway.steps[0].scope);
    });
  });

  describe("stepIndex", function(){
    it("should return the idx of the step", function(){
      expect(pathway.stepIndex(pathway.steps[1].api_name)).toBe(1);
    });

    it("should throw an exception if there is no step by that name", function(){
      expect(function(){ pathway.stepIndex("non existent") }).toThrow();
    });
  });

  describe("showNext", function(){
    it("should return true", function(){
      expect(pathway.showNext({})).toBe(true);
    });
  });
});
