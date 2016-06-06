//
// Unit tests for our FilterLoader Service
//
describe('filtersLoader', function(){
    "use strict";

    var filtersLoader, mockWindow, $httpBackend

    beforeEach(function(){
        module('opal.services');
        module('opal.controllers');

        mockWindow = { alert: jasmine.createSpy() };

        module(function($provide){
            $provide.value('$window', mockWindow);
        });

        inject(function($injector){
            filtersLoader = $injector.get('filtersLoader');
            $httpBackend  = $injector.get('$httpBackend');
        });

    });

    describe('query', function(){

        it('should save existing filters', function(){
            $httpBackend.whenGET('/search/filters/').respond([{id: 1, name: 'afilter'}]);

            filtersLoader()
            $rootScope.$apply();
            $httpBackend.flush();
        });

        it('should handle errors', function(){
            $httpBackend.whenGET('/search/filters/').respond(500, 'failure');

            filtersLoader();

            $rootScope.$apply();
            $httpBackend.flush();
            expect(mockWindow.alert).toHaveBeenCalled();
        });

    });

});
