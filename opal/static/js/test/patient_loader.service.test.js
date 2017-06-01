//
// Unit tests for our patient loader service
//
describe('patientLoader', function() {
    "use strict";

    var $httpBackend, $route, $rootScope;
    var mockWindow;
    var patientLoader;

    var response = {
        demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}],
        episodes: {
            122: {
                id: 122, start: "20/01/2016", end: "20/02/2016",
                demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]},
            123: {
                id: 123, start: "20/01/2016", end: undefined,
                demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]},
            124: {
                id: 124, start: undefined, end: "20/03/2016",
                demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]},
            125: {
                id: 125, start: undefined, end: undefined,
                demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]}
        }
    };

    beforeEach(function(){
        module('opal.services');

        mockWindow = { alert: jasmine.createSpy() };

        module(function($provide) {
            $provide.value('$window', mockWindow);
        });

        inject(function($injector){
            patientLoader = $injector.get('patientLoader');
            $httpBackend  = $injector.get('$httpBackend');
            $route        = $injector.get('$route');
            $rootScope    = $injector.get('$rootScope');
        });

        $httpBackend.expectGET('/api/v0.1/record/').respond({});
        $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});

        $route.current = { params: { patient_id: '123' } };
    });

    afterEach(function(){
      $rootScope.$apply();
      $httpBackend.flush();
      $httpBackend.verifyNoOutstandingRequest();
      $httpBackend.verifyNoOutstandingExpectation();
    });


    describe('load patients', function() {
      it('should load a patient from route params', function() {
        $httpBackend.expectGET('/api/v0.1/patient/123/').respond(response);
        patientLoader().then(function(patient){
          expect(patient.demographics[0].first_name).toEqual("Sue");
        });
      });

      it('should load a patient an argument', function() {
        $httpBackend.expectGET('/api/v0.1/patient/124/').respond(response);
        patientLoader("124").then(function(patient){
          expect(patient.demographics[0].first_name).toEqual("Sue");
        });
      });
    });

    describe('patient API errors', function() {
      it('should alert() the user', function() {
        $httpBackend.expectGET('/api/v0.1/patient/123/').respond(500);
        patientLoader().then(function(patient){
          expect(mockWindow.alert).toHaveBeenCalledWith('Patient could not be loaded');
        });
      });
    });

    describe('No patient id found', function() {
        it('should fail quiently if we have no way of knowing the patient ID', function() {
            $route.current.params = {};
            patientLoader().then(function(p){
                expect(p).toEqual([]);
            });
        });

    });
});
