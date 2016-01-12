//
// Unit tests for our Flow Service
//

describe('Flow ', function(){
    "use strict";
    var options, the_flow, Flow, $httpBackend, $modal, $rootScope;

    beforeEach(function(){

        module('opal.services');
        module('opal.controllers');

        angular.module('opal.controllers').controller('EnterCtrl', function(){});
        angular.module('opal.controllers').controller('ExitCtrl', function(){});

        options = {};
        the_flow = {
            default: {
                enter: {
                    controller: 'EnterCtrl',
                    template  : '/templates/enter',
                },
                exit : {
                    controller: 'ExitCtrl',
                    template  : '/templates/exit',
                }
            }
        }

        inject(function($injector){
            Flow         = $injector.get('Flow');
            $modal       = $injector.get('$modal');
            $rootScope   = $injector.get('$rootScope');
            $httpBackend = $injector.get('$httpBackend');
        });

        $httpBackend.whenGET('/api/v0.1/flow/').respond(the_flow);
        $httpBackend.whenGET('/templates/enter').respond('<notarealtemplate>');
        $httpBackend.whenGET('/templates/exit').respond('<notarealtemplate>');

        spyOn($modal, 'open').and.callThrough();

    });

    describe('enter', function(){
        it('should pass through to the correct controller', function(){
            var call_args;

            Flow('enter', options, {current_tags: { tag: "Micro-Ortho" }});

            $rootScope.$apply();
            $httpBackend.flush();

            call_args = $modal.open.calls.mostRecent().args;
            expect(call_args.length).toBe(1);
            expect(call_args[0].templateUrl).toBe('/templates/enter');
            expect(call_args[0].controller).toBe('EnterCtrl');

        });
    });

    describe('exit', function(){
        it('should pass through to the correct controller', function(){
            var call_args;

            Flow('exit', options, {current_tags: { tag: "Micro-Ortho" }});

            $rootScope.$apply();
            $httpBackend.flush();

            call_args = $modal.open.calls.mostRecent().args;
            expect(call_args.length).toBe(1);
            expect(call_args[0].templateUrl).toBe('/templates/exit');
            expect(call_args[0].controller).toBe('ExitCtrl');

        });

    });

})
