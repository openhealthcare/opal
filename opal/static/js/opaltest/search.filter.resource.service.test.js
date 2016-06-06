//
// Unit tests for our FilterResource Service
//
describe('FilterResource', function(){
    "use strict";

    var FilterResource, $httpBackend

    beforeEach(function(){
        module('opal.services');
        module('opal.controllers');

        inject(function($injector){
            FilterResource = $injector.get('FilterResource');
            $httpBackend   = $injector.get('$httpBackend');
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
