//
// Unit tests for our Flow Service
//

describe('Flow ', function(){
    "use strict";
    var $httpBackend, $modal, $rootScope;
    var options, Flow, Metadata, Referencedata;

    beforeEach(function(){

        module('opal.services');
        module('opal.controllers');

        inject(function($injector){
            Flow          = $injector.get('Flow');
            Referencedata = $injector.get('Referencedata');
            Metadata      = $injector.get('Metadata');
            $modal        = $injector.get('$modal');
            $rootScope    = $injector.get('$rootScope');
            $httpBackend  = $injector.get('$httpBackend');
        });

        spyOn($modal, 'open').and.returnValue({result: null});
    });

    describe('enter', function(){
        it('should call the modal with the enter flow', function(){
            Flow.enter({hospital_number: '555-456'});
            var args = $modal.open.calls.mostRecent().args;
            expect(args[0].controller).toEqual('HospitalNumberCtrl');
            expect(args[0].templateUrl).toEqual('/templates/modals/hospital_number.html/');
            var resolves = args[0].resolve;
            expect(resolves.tags()).toEqual(undefined);
            expect(resolves.hospital_number()).toEqual('555-456');
            expect(resolves.referencedata(Referencedata)).toEqual(Referencedata)
            expect(resolves.metadata(Metadata)).toEqual(Metadata)
        });
    });

    describe('exit', function(){
        it('should call exit', function(){
            Flow.exit('episode', {current_tags: {}});
            var args = $modal.open.calls.mostRecent().args;
            expect(args[0].controller).toEqual('DischargeEpisodeCtrl');
            expect(args[0].templateUrl).toEqual('/templates/modals/discharge_episode.html/');
            var resolves = args[0].resolve;
            expect(resolves.tags()).toEqual({});
            expect(resolves.episode()).toEqual('episode');
            expect(resolves.referencedata(Referencedata)).toEqual(Referencedata)
            expect(resolves.metadata(Metadata)).toEqual(Metadata)
        });

    });

})
