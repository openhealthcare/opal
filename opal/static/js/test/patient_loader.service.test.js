//
// Unit tests for our patient loader service
//
describe('patientLoader', function() {
  "use strict";

  var $httpBackend, $route, $rootScope;
  var patientLoader;

  var response = {
    demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}],
    episodes: {
      122: {id: 122, start: "20/01/2016", end: "20/02/2016", demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]},
      123: {id: 123, start: "20/01/2016", end: undefined, demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]},
      124: {id: 124, start: undefined, end: "20/03/2016", demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]},
      125: {id: 125, start: undefined, end: undefined, demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]}
    }
  };

  beforeEach(function(){
    module('opal.services');

    inject(function($injector){
      patientLoader = $injector.get('patientLoader');
      $httpBackend  = $injector.get('$httpBackend');
      $route        = $injector.get('$route');
      $rootScope    = $injector.get('$rootScope');
    });

    $httpBackend.expectGET('/api/v0.1/record/').respond({});
    $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
    $httpBackend.expectGET('/api/v0.1/patient/123/').respond(response);
    $route.current = { params: { patient_id: '123' } };
  });

  afterEach(function(){
    $rootScope.$apply();
    $httpBackend.flush();
  });

  describe('load patients', function() {
    it('should load some patients', function() {
      patientLoader().then(function(patient){
        expect(patient.demographics[0].first_name).toEqual("Sue");
      });
    });
  });
});
