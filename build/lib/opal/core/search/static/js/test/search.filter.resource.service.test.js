//
// Unit tests for our FilterResource Service
//
describe('FilterResource', function(){
    "use strict";

    var $rootScope, $httpBackend
    var FilterResource;

    beforeEach(function(){
        module('opal.services');
        module('opal.controllers');

        inject(function($injector){
            $httpBackend   = $injector.get('$httpBackend');
            $rootScope     = $injector.get('$rootScope');
            FilterResource = $injector.get('FilterResource');
        });

    });

    describe('resource', function(){

        it('should hit the API', function(){
            $httpBackend.whenGET('/search/filters/').respond([]);
            FilterResource.query(function(resources){})
            $rootScope.$apply();
            $httpBackend.flush();
        });

    });

});
