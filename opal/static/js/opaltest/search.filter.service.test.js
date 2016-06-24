//
// Unit tests for our Filter Service
//
describe('Filter', function(){
    "use strict";

    var Filter, mockWindow, $httpBackend

    beforeEach(function(){
        module('opal.services');
        module('opal.controllers');

        mockWindow = { alert: jasmine.createSpy() };

        module(function($provide){
            $provide.value('$window', mockWindow);
        });

        inject(function($injector){
            Filter       = $injector.get('Filter');
            $httpBackend = $injector.get('$httpBackend');
        });

    });

    describe('save()', function(){

        it('should save existing filters', function(){
            $httpBackend.whenPUT('/search/filters/1/').respond({value: 'success'});

            var filter = new Filter({id: 1, name: 'myfilter', criteria: []})
            filter.save({id: 1, name: 'myrenamedfilter', criteria: []})

            $rootScope.$apply();
            $httpBackend.flush();
        });

        it('should save new filters', function(){
            $httpBackend.whenPOST('/search/filters/').respond({value: 'success'});

            var filter = new Filter()
            filter.save({name: 'mynewfilter', criteria: []})

            $rootScope.$apply();
            $httpBackend.flush();
        });

        it('should handle errors', function(){
            $httpBackend.whenPOST('/search/filters/').respond(500, 'failure');

            var filter = new Filter()
            filter.save({name: 'mynewfilter', criteria: []})

            $rootScope.$apply();
            $httpBackend.flush();
            expect(mockWindow.alert).toHaveBeenCalled();
        });

        it('should handle 409 errors', function(){
            $httpBackend.whenPOST('/search/filters/').respond(409, 'failure');

            var filter = new Filter()
            filter.save({name: 'mynewfilter', criteria: []})

            $rootScope.$apply();
            $httpBackend.flush();
            expect(mockWindow.alert).toHaveBeenCalled();
        });

    });

    describe('destroy()', function(){

        it('should hit the API', function(){
            $httpBackend.whenDELETE('/search/filters/3/').respond('success');
            var filter = new Filter({name: 'myfilter', id: 3});
            filter.destroy();
            $rootScope.$apply();
            $httpBackend.flush();
        });

        it('should handle errors', function(){
            $httpBackend.whenDELETE('/search/filters/3/').respond(500, 'success');
            var filter = new Filter({name: 'myfilter', id: 3});
            filter.destroy();
            $rootScope.$apply();
            $httpBackend.flush();
            expect(mockWindow.alert).toHaveBeenCalled();
        });

    });

});
