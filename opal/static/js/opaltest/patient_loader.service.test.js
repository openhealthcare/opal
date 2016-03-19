//
// Unit tests for our patient loader service
//
describe('patientLoader', function() {
    var $httpBackend, $route, $rootScope;
    var patientLoader;

    beforeEach(function(){
        module('opal.services');

        inject(function($injector){
            patientLoader = $injector.get('patientLoader');
            $httpBackend  = $injector.get('$httpBackend');
            $route        = $injector.get('$route');
            $rootScope    = $injector.get('$rootScope');
        });

    });

    describe('load patients', function() {

        it('should load some patients', function() {
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            $httpBackend.expectGET('/api/v0.1/record/').respond({});
            $httpBackend.expectGET('/api/v0.1/patient/123/').respond({});
            $route.current = { params: { patient_id: '123' } };
            patientLoader();
            $rootScope.$apply();
            $httpBackend.flush()
        });

    });

});
