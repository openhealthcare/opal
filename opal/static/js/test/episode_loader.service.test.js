//
// Unit tests for our episod loader
//
describe('episodeLoader', function() {
    "use strict"

    var $httpBackend, $route, $rootScope, $window;
    var episodeLoader, episodeData;

    episodeData = {
        demographics: [{patient_id: 1234}],
        tagging: [{}]
    }

    beforeEach(function(){
        module('opal');

        inject(function($injector){
            episodeLoader = $injector.get('episodeLoader');
            $route        = $injector.get('$route');
            $rootScope    = $injector.get('$rootScope');
            $httpBackend  = $injector.get('$httpBackend');
            $window       = $injector.get('$window');
        });

        $httpBackend.expectGET('/api/v0.1/userprofile/').respond({})
        $httpBackend.expectGET('/api/v0.1/record/').respond({})
    })


    describe('fetch episodes', function() {

        it('should hit the api', function() {
            $route.current = { params: { id: 123 } }

            $httpBackend.expectGET('/api/v0.1/episode/123/').respond(episodeData);
            var promise = episodeLoader();
            $rootScope.$apply();
            $httpBackend.flush();
        });

        it('should alert on a nonexistant episode', function() {
            $route.current = { params: { id: 123 } }
            spyOn($window, 'alert');

            $httpBackend.expectGET('/api/v0.1/episode/123/').respond(500);
            var promise = episodeLoader();
            $rootScope.$apply();
            $httpBackend.flush();
            expect($window.alert).toHaveBeenCalledWith('Episode could not be loaded')
        });

    });

});
