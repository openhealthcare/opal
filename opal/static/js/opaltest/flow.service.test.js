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

        spyOn($modal, 'open').and.returnValue({result: null});
    });

    describe('enter', function(){
        it('should call the modal with the enter flow', function(){
            Flow.enter({}, {hospital_number: '555-456'});
            var args = $modal.open.calls.mostRecent().args;
            expect(args[0].controller).toEqual('HospitalNumberCtrl');
            expect(args[0].templateUrl).toEqual('/templates/modals/hospital_number.html/');
            var resolves = args[0].resolve;
            expect(resolves.options()).toEqual({});
            expect(resolves.tags()).toEqual(undefined);
            expect(resolves.hospital_number()).toEqual('555-456');
        });
    });

    describe('exit', function(){
        it('should call exit', function(){
            Flow.exit('episode', 'options', {current_tags: {}});
            var args = $modal.open.calls.mostRecent().args;
            expect(args[0].controller).toEqual('DischargeEpisodeCtrl');
            expect(args[0].templateUrl).toEqual('/templates/modals/discharge_episode.html/');
            var resolves = args[0].resolve;
            expect(resolves.options()).toEqual('options');
            expect(resolves.tags()).toEqual({});
            expect(resolves.episode()).toEqual('episode');
        });

    });

})
