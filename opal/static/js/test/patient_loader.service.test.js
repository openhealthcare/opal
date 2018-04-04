//
// Unit tests for our patient loader service
//
describe('patientLoader', function() {
    "use strict";

    var $httpBackend, $route, $rootScope, response;
    var mockWindow, opalTestHelper;
    var patientLoader;

    beforeEach(function(){
        module('opal.services');
        module('opal.test');

        mockWindow = { alert: jasmine.createSpy() };

        module(function($provide) {
            $provide.value('$window', mockWindow);
        });


        inject(function($injector){
            patientLoader = $injector.get('patientLoader');
            $httpBackend  = $injector.get('$httpBackend');
            $route        = $injector.get('$route');
            $rootScope    = $injector.get('$rootScope');
            opalTestHelper    = $injector.get('opalTestHelper');
        });

        response = opalTestHelper.getPatientData();

        $route.current = { params: { patient_id: '123' } };
    });

    afterEach(function(){
      $httpBackend.verifyNoOutstandingRequest();
      $httpBackend.verifyNoOutstandingExpectation();
    });


    describe('load patients', function() {
      it('should load a patient from route params', function() {
        $httpBackend.expectGET('/api/v0.1/patient/123/').respond(response);
        $httpBackend.expectGET('/api/v0.1/record/').respond({});
        patientLoader().then(function(patient){
          expect(patient.demographics[0].first_name).toEqual("John");
        });
        $rootScope.$apply();
        $httpBackend.flush();
      });

      it('should load a patient an argument', function() {
        $httpBackend.expectGET('/api/v0.1/patient/124/').respond(response);
        $httpBackend.expectGET('/api/v0.1/record/').respond({});
        patientLoader("124").then(function(patient){
          expect(patient.demographics[0].first_name).toEqual("John");
        });
        $rootScope.$apply();
        $httpBackend.flush();
      });
    });

    describe('patient API errors', function() {

      it('should alert() the user', function() {
        $httpBackend.expectGET('/api/v0.1/patient/123/').respond(500);
        $httpBackend.expectGET('/api/v0.1/record/').respond({});
        patientLoader().then(function(patient){
          expect(mockWindow.alert).toHaveBeenCalledWith('Patient could not be loaded');
        });
        $rootScope.$apply();
        $httpBackend.flush();
      });

      it('should resolve with null', function() {
        $httpBackend.expectGET('/api/v0.1/patient/123/').respond(500);
        $httpBackend.expectGET('/api/v0.1/record/').respond({});
        patientLoader().then(function(patient){
          expect(patient).toBe(null);
        });
        $rootScope.$apply();
        $httpBackend.flush();
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
