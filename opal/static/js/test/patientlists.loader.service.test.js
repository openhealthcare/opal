describe('PatientListLoaderTest', function(){
    "use strict";

    var patientListLoader, Episode, $route, $rootScope, $httpBackend;

    beforeEach(function(){
        module('opal');
        inject(function($injector){
            patientListLoader = $injector.get('patientListLoader');
            Episode           = $injector.get('Episode');
            $route            = $injector.get('$route');
            $rootScope        = $injector.get('$rootScope');
            $httpBackend      = $injector.get('$httpBackend');
        });

        $httpBackend.expectGET('/api/v0.1/record/').respond({})
    })

    it('should fetch the episodes for a list', function(){
        var result

        var episodedata = {id: 1, demographics: [{patient_id: 1, name: 'Jane'}] };

        $route.current = {params: {slug: 'mylist'}}
        $httpBackend.whenGET('/api/v0.1/patientlist/mylist/').respond([episodedata])
        patientListLoader().then(function(r){ result = r; })

        $rootScope.$apply();
        $httpBackend.flush();

        expect(result.status).toEqual('success');
        expect(result.data[1].id).toEqual(1);
        expect(result.data[1].demographics[0].name).toEqual('Jane');
    });


    it('should resolve an error for nonexistant lists', function(){
        var result

        $route.current = {params: {slug: 'mylist'}}
        $httpBackend.whenGET('/api/v0.1/patientlist/mylist/').respond(404, {error: "NOT FOUND"});
        patientListLoader().then(function(r){ result = r; })

        $rootScope.$apply();
        $httpBackend.flush();

        expect(result.status).toEqual('error');
        expect(result.data).toEqual({error: "NOT FOUND"});
    });

    it('should look up lists based on slug if passed in', function(){
      $route.current = {params: {slug: 'mylist'}};
      $httpBackend.whenGET('/api/v0.1/patientlist/yourlist/').respond([]);
      patientListLoader("yourlist");
      $rootScope.$apply();
      $httpBackend.flush();
    });
});
