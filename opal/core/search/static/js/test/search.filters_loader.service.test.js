//
// Unit tests for our FilterLoader Service
//
describe('filtersLoader', function(){
    "use strict";

    var $rootScope, $httpBackend
    var filtersLoader, mockWindow;

    beforeEach(function(){
        module('opal.services');
        module('opal.controllers');

        mockWindow = { alert: jasmine.createSpy() };

        module(function($provide){
            $provide.value('$window', mockWindow);
        });

        inject(function($injector){
            $rootScope    = $injector.get('$rootScope');
            $httpBackend  = $injector.get('$httpBackend');
            filtersLoader = $injector.get('filtersLoader');
        });

    });

    describe('query', function(){

        it('should save existing filters', function(){
            $httpBackend.whenGET('/search/filters/').respond([{id: 1, name: 'afilter'}]);

            filtersLoader.load();
            $httpBackend.flush();
            $rootScope.$apply();
        });

        it('should handle errors', function(){
            $httpBackend.whenGET('/search/filters/').respond(500, 'failure');

            filtersLoader.load();
            $httpBackend.flush();
            $rootScope.$apply();
            expect(mockWindow.alert).toHaveBeenCalled();
        });

    });

});
