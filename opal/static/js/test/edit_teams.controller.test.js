describe('EditTeamsCtrl', function(){
    "use strict";

    var $scope, $rootScope, $httpBackend, $window, $modal, $controller;
    var Episode;
    var UserProfile;
    var modalInstance, ngProgressLite;
    var episode, opalTestHelper;

    beforeEach(function(){
        module('opal.controllers');
        module('opal.test');

        inject(function($injector){
            $httpBackend     = $injector.get('$httpBackend');
            $rootScope       = $injector.get('$rootScope');
            $scope           = $rootScope.$new();
            $window          = $injector.get('$window');
            $controller      = $injector.get('$controller');
            $modal           = $injector.get('$modal');
            Episode          = $injector.get('Episode');
            opalTestHelper   = $injector.get('opalTestHelper');
            ngProgressLite   = $injector.get('ngProgressLite');
        });

        UserProfile = opalTestHelper.getUserProfileLoader();

        modalInstance = $modal.open({template: 'notatemplate'});
        episode = opalTestHelper.newEpisode($rootScope);

        episode.tagging = [
                {
                    save: function(a){
                        return {then: function(fn, fn2) { fn(); }}
                    },
                    makeCopy: function(){
                      return {tropical: true};
                    }
                }
        ];

        $controller('EditTeamsCtrl', {
            $scope: $scope,
            $window: $window,
            $modalInstance: modalInstance,
            episode: episode,
            UserProfile: UserProfile
        });
    });

    describe('Setup', function() {

        it('should have an editing object', function() {
            expect($scope.editing).toEqual({tagging: {tropical: true}});
        });

        it('should put profile and editingname on the scope', function(){
          expect(UserProfile.load).toHaveBeenCalled();
          expect($scope.editingName).toBe("John Smith");
          expect(!!$scope.profile).toBe(true);
        });

        it('should not set an empty object if there are no tags', function(){
          episode.tagging = [];
          $controller('EditTeamsCtrl', {
              $scope: $scope,
              $window: $window,
              $modalInstance: modalInstance,
              episode: episode
          });
            expect($scope.editing).toEqual({tagging: {}});
        });

        it('should fetch the options', function() {
            expect($scope.profile).toEqual(opalTestHelper.getUserProfile());
            expect(UserProfile.load).toHaveBeenCalled();
        });
    });

    describe('save()', function() {

        it('should save', function() {
            spyOn(modalInstance, 'close');
            $scope.save('close');
            $rootScope.$apply();
            expect(modalInstance.close).toHaveBeenCalledWith('close');
        });

        it('should reset the progressbar if we error', function() {
            spyOn(ngProgressLite, 'done');
            episode.tagging[0].save = function(a){
                        return {then: function(fn, fn2) { fn2(); }}
                    }
            $scope.save('close');
            $rootScope.$apply();
            expect(ngProgressLite.done).toHaveBeenCalledWith()
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
