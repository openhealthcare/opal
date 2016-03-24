//
// Unit tests for our Flow Service
//

describe('Flow ', function(){
    "use strict";
    var options, Flow, $httpBackend, $modal, $rootScope;

    beforeEach(function(){

        module('opal.services');
        module('opal.controllers');

        inject(function($injector){
            Flow         = $injector.get('Flow');
            $modal       = $injector.get('$modal');
            $rootScope   = $injector.get('$rootScope');
            $httpBackend = $injector.get('$httpBackend');
        });

        spyOn($modal, 'open');

    });

    describe('enter', function(){
        it('should call enter', function(){

        });
    });

    describe('exit', function(){
        it('should call exit', function(){

        });

    });

})
