describe('DischargeEpisodeCtrl', function(){
    "use strict";

    var $scope, $modal, $httpBackend, $window, $rootScope, $controller;
    var Episode, opalTestHelper;
    var modalInstance, episodeData, episode, tags, fields, records;
    var mkcontroller;

    beforeEach(function(){
        module('opal.controllers');
        module('opal.test');

        inject(function($injector){
            $rootScope   = $injector.get('$rootScope');
            $window      = $injector.get('$window');
            $controller  = $injector.get('$controller');
            $httpBackend = $injector.get('$httpBackend');
            $modal       = $injector.get('$modal');
            Episode      = $injector.get('Episode');
            opalTestHelper = $injector.get('opalTestHelper')
        });

        episodeData = opalTestHelper.getEpisodeData()
        episodeData.end = null;
        episode = opalTestHelper.newEpisode($rootScope, episodeData);

        modalInstance = $modal.open({template: 'notatemplate'});
        tags = {};

        mkcontroller = function(tags, _episode){
          _episode = _episode || episode;
          $scope = $rootScope.$new();

          $controller('DischargeEpisodeCtrl', {
              $scope: $scope,
              $window: $window,
              $modalInstance: modalInstance,
              episode: _episode,
              tags: tags
          });
        }
        mkcontroller(tags)
    });

    describe('Set up the controller', function(){
        it('should have the current and new categories', function() {
            expect($scope.editing.category).toEqual('Discharged');
        });


        it('should handle arbitrary categories', function() {
            episode.location[0].category = 'Dead';
            mkcontroller();
            expect($scope.editing.category).toEqual('Dead');
        });

        it('should set the tags to mine', function() {
            expect($scope.currentTag).toEqual('mine');
        });

        it('should set the tags to tags when they exist', function() {
            mkcontroller({tag: 'infection', subtag: 'tropical'});
            expect($scope.currentTag).toEqual('infection');
            expect($scope.currentSubTag).toEqual('tropical');
        });

        it('should set the discharge date/end from the episode if it exists', function() {
            episode.end = new Date(2000, 0, 1);
            mkcontroller();
            expect($scope.editing.end).toEqual(new Date(2000, 0, 1));
        });

        it('should set the new category to unfollow if we are a review patient', function() {
            var alteredEpisodeData = angular.copy(episodeData);
            alteredEpisodeData.location[0].category = 'Review';
            mkcontroller(tags, new Episode(alteredEpisodeData));
            expect($scope.editing.category).toEqual('Unfollow');
        });

    });

    describe('discharge()', function() {

        it('should discharge the patient', function() {

            $httpBackend.expectPUT('/api/v0.1/tagging/123/').respond({});
            $httpBackend.expectPOST('/api/v0.1/location/').respond({});
            $httpBackend.expectPUT('/api/v0.1/episode/123/').respond(episodeData);
            spyOn(modalInstance, 'close')

            $scope.discharge();

            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingRequest();
            $httpBackend.verifyNoOutstandingExpectation();

            expect(modalInstance.close).toHaveBeenCalledWith('discharged')
        });

        it('should remove the end if category is Unfollow', function() {
            $httpBackend.expectPUT('/api/v0.1/tagging/123/').respond({});
            $httpBackend.expectPOST('/api/v0.1/location/').respond({});

            var expected = {
              id:123,
              start: "19/11/2013",
              end: null,
              category_name:"Inpatient",
            };
            $httpBackend.expectPUT('/api/v0.1/episode/123/', expected).respond(episodeData);

            var alteredEpisodeData = angular.copy(episodeData);
            alteredEpisodeData.end = moment();
            mkcontroller(tags, new Episode(alteredEpisodeData));
            $scope.editing.category = "Unfollow";
            $scope.discharge();
            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingRequest();
            $httpBackend.verifyNoOutstandingExpectation();
        });

        it('should use the end from editing if the category is not Unfollow', function() {
            $httpBackend.expectPUT('/api/v0.1/tagging/123/').respond({});
            $httpBackend.expectPOST('/api/v0.1/location/').respond({});
            var alteredEpisodeData = angular.copy(episodeData);
            alteredEpisodeData.end = moment(new Date(2016, 6, 6));

            var expected = {
              id: 123,
              category_name: "Inpatient",
              start: "19/11/2013",
              end: "06/07/2016"
            };
            $httpBackend.expectPUT('/api/v0.1/episode/123/', expected).respond(alteredEpisodeData);
            mkcontroller(tags, new Episode(alteredEpisodeData));
            $scope.editing.category = "Followup";
            $scope.discharge();
            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingRequest();
            $httpBackend.verifyNoOutstandingExpectation();
        });

        it('should nuke the current end tag if there is one', function() {
            var tags = {tag:'inpatients', subtag: 'icu'};
            var alteredEpisodeData = angular.copy(episodeData);
            alteredEpisodeData.tagging[0].inpatients = true;
            alteredEpisodeData.tagging[0].icu = true;

            mkcontroller(tags, new Episode(alteredEpisodeData))
                expectedTagging
            var expectedTagging = {
                id: 123,
                icu: false,
                tropical: true,
                mine: true
            };

            $httpBackend.expectPUT('/api/v0.1/tagging/123/', expectedTagging).respond({});
            $httpBackend.expectPOST('/api/v0.1/location/').respond({});
            $httpBackend.expectPUT('/api/v0.1/episode/123/').respond(episodeData);
            $scope.discharge();
            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingRequest();
            $httpBackend.verifyNoOutstandingExpectation();

        });

    });

    describe('cancel()', function(){

        it('should close with null', function(){
            spyOn(modalInstance, 'close');
            $scope.cancel();
            expect(modalInstance.close).toHaveBeenCalledWith('cancel');
        });

    })

});
