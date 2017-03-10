//
// Unit tests for our Flow Service
//

describe('Flow ', function(){
    "use strict";
    var $httpBackend, $modal, $rootScope;
    var options, Flow, Referencedata;
    var metadata = {load: function(){}};
    var referencedata = {load: function(){}};

    beforeEach(function(){

        module('opal.services');
        module('opal.controllers');
        spyOn(metadata, "load").and.returnValue("some metadata");
        spyOn(referencedata, "load").and.returnValue("some reference data");

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
