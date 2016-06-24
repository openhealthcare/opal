//
// Unit tests for our patient loader service
//
describe('patientLoader', function() {
    var $httpBackend, $route, $rootScope;
    var patientLoader;

    response = {
        demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}],
        episodes: {
            123: {demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]}
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

    });

    describe('load patients', function() {
        it('should load some patients', function() {
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            $httpBackend.expectGET('/api/v0.1/record/').respond({});
            $httpBackend.expectGET('/api/v0.1/patient/123/').respond(response);
            $route.current = { params: { patient_id: '123' } };
            patientLoader().then(function(patient){
                expect(patient.recordEditor).toEqual(patient.episodes[0].recordEditor);
                patient.episodes[0].demographics[0].first_name = "Jane"
                expect(patient.demographics[0].first_name).toEqual("Jane");
            });

            $rootScope.$apply();
            $httpBackend.flush()
        });

    });

});
