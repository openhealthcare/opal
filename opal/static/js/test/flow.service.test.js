//
// Unit tests for our Flow Service
//

describe('Flow ', function(){
    "use strict";
    var $httpBackend, $modal, $rootScope;
    var options, Flow, Referencedata;
    var metadata = {load: function(){}};
    var referencedata = {load: function(){}};
    var mock_flow_service;

    beforeEach(function(){

        module('opal.services');
        module('opal.controllers');
        spyOn(metadata, "load").and.returnValue("some metadata");
        spyOn(referencedata, "load").and.returnValue("some reference data");
        mock_flow_service = null;

        module(function($provide){
            $provide.value('OPAL_FLOW_SERVICE', mock_flow_service);
        });

        inject(function($injector){
            Flow          = $injector.get('Flow');
            $modal        = $injector.get('$modal');
            $rootScope    = $injector.get('$rootScope');
            $httpBackend  = $injector.get('$httpBackend');
        });

        spyOn($modal, 'open').and.returnValue({result: null});
    });

    describe('enter', function(){
        it('should call the modal with the enter flow', function(){
            Flow.enter({hospital_number: '555-456'}, {some: "context"});
            var args = $modal.open.calls.mostRecent().args;
            expect(args[0].controller).toEqual('HospitalNumberCtrl');
            expect(args[0].templateUrl).toEqual('/templates/modals/hospital_number.html/');
            var resolves = args[0].resolve;
            expect(resolves.tags()).toEqual(undefined);
            expect(resolves.hospital_number()).toEqual('555-456');
            expect(resolves.referencedata(referencedata)).toEqual("some reference data");
            expect(resolves.metadata(metadata)).toEqual("some metadata");
            expect(resolves.context()).toEqual({some: "context"});
        });
    });

    describe('exit', function(){
        it('should call exit', function(){
            Flow.exit('episode', {current_tags: {}}, {some: "context"});
            var args = $modal.open.calls.mostRecent().args;
            expect(args[0].controller).toEqual('DischargeEpisodeCtrl');
            expect(args[0].templateUrl).toEqual('/templates/modals/discharge_episode.html/');
            var resolves = args[0].resolve;
            expect(resolves.tags()).toEqual({});
            expect(resolves.episode()).toEqual('episode');
            expect(resolves.referencedata(referencedata)).toEqual("some reference data");
            expect(resolves.metadata(metadata)).toEqual("some metadata");

            expect(resolves.context()).toEqual({some: "context"});
        });
    });
});


///
/// For reasons beyond my comprehension, it seems impossible to
/// re-set these mocks/injectors/providers within the same describe block, so we
/// are starting again with a fresh context.
///
describe('Flow ', function(){
    "use strict";
    var $httpBackend, $modal, $rootScope;
    var options, Flow, Referencedata;
    var metadata = {load: function(){}};
    var referencedata = {load: function(){}};
    var mock_flow_service;

    beforeEach(function(){

        module('opal.services');
        module('opal.controllers');
        spyOn(metadata, "load").and.returnValue("some metadata");
        spyOn(referencedata, "load").and.returnValue("some reference data");
        mock_flow_service =  {
            enter: jasmine.createSpy().and.returnValue(
                {
                    'controller': 'HospitalNumberCtrl',
                    'template'  : '/templates/modals/hospital_number.html/'
                }
            ),
            exit: jasmine.createSpy().and.returnValue(
                {
                    'controller': 'DischargeEpisodeCtrl',
                    'template'  : '/templates/modals/discharge_episode.html/'
                }
            )
        };

        module(function($provide){
            $provide.value('TestCustomFlowService', mock_flow_service);
            $provide.value('OPAL_FLOW_SERVICE', 'TestCustomFlowService');
        });

        inject(function($injector){
            Flow          = $injector.get('Flow');
            $modal        = $injector.get('$modal');
            $rootScope    = $injector.get('$rootScope');
            $httpBackend  = $injector.get('$httpBackend');
        });

    });


    describe('with custom service', function() {

        describe('enter', function() {
            it('should call the custom service', function() {
                Flow.enter({hospital_number: '555-456'}, {some: "context"});
                expect(mock_flow_service.enter).toHaveBeenCalled();
            });

        });

        describe('exit', function() {

            it('should call the custom service', function() {
                Flow.exit({hospital_number: '555-456'}, {some: "context"});
                expect(mock_flow_service.exit).toHaveBeenCalled();
            });

            it('should resolve the promise with the result of the modal', function(){
                spyOn($modal, 'open').and.returnValue({result: "discharged"});
                var exitPromise = Flow.exit({hospital_number: '555-456'}, {some: "context"});
                var expected;

                exitPromise.then(function(x){
                  expected = x;
                });
                $rootScope.$apply();
                expect(expected).toBe('discharged');
            });

        });


    });
});
