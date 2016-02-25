describe('PatientListLoaderTest', function(){
    "use strict";

    var patientListLoader, $route, $rootScope, $httpBackend;

    beforeEach(function(){
        module('opal');
        inject(function($injector){
            patientListLoader = $injector.get('patientListLoader');
            $route            = $injector.get('$route');
            $rootScope        = $injector.get('$rootScope');
            $httpBackend      = $injector.get('$httpBackend');
        });

        $httpBackend.expectGET('/api/v0.1/userprofile/').respond({})
        $httpBackend.expectGET('/api/v0.1/record/').respond({})
    })

    it('should fetch the episodes for a list', function(){
        var result

        $route.current = {params: {list: 'mylist'}}
        $httpBackend.whenGET('/api/v0.1/patientlist/mylist').respond([])
        patientListLoader().then(function(r){ result = r; })

        $rootScope.$apply();
        $httpBackend.flush();

        expect(result.status).toEqual('success');
        expect(result.data).toEqual({});
    });


    it('should resolve an error for nonexistant lists', function(){
        var result

        $route.current = {params: {list: 'mylist'}}
        $httpBackend.whenGET('/api/v0.1/patientlist/mylist').respond(404, {error: "NOT FOUND"});
        patientListLoader().then(function(r){ result = r; })

        $rootScope.$apply();
        $httpBackend.flush();

        expect(result.status).toEqual('error');
        expect(result.data).toEqual({error: "NOT FOUND"});
    });
})
