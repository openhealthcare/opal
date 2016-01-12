describe('PatientHistoryCtrl', function (){
    "use strict";

    var $controller, $scope, $modalInstance, $httpBackend, $rootScope;
    var $modal, $location;
    var Episode, controller;
    var episode, episode_history;

    beforeEach(module('opal.controllers'));

    beforeEach(inject(function($injector){
        $rootScope   = $injector.get('$rootScope');
        $scope       = $rootScope.$new();
        $modal       = $injector.get('$modal');
        $controller  = $injector.get('$controller');
        $httpBackend = $injector.get('$httpBackend');
        Episode      = $injector.get('Episode');
        $location    = $injector.get('$location');

        $modalInstance = $modal.open({template: 'Not a real template'});
        episode_history = [1,2,3,4];
        episode = new Episode({
          id: 33,
          episode_history: episode_history,
          demographics: [{
              id: 101,
              name: 'John Smith',
              date_of_birth: '1980-07-31',
              patient_id: 102
          }]
        });

        controller = $controller('PatientHistoryCtrl', {
            $scope        : $scope,
            $modalInstance: $modalInstance,
            episode       : episode
        });

    }));

    it('sets up state', function (){
        expect($scope.episode).toBe(episode);
        expect($scope.episode_history).toEqual([4,3,2,1]);
    });

    describe('jump_to_episode()', function (){

        beforeEach(function(){
            spyOn($location, 'path');
            spyOn($modalInstance, 'close');
        });

        it('should jump', function (){
            $scope.jump_to_episode({id: 32})
            expect($modalInstance.close).toHaveBeenCalledWith('cancel');
            expect($location.path).toHaveBeenCalledWith('/episode/32')
        });

        it('should not jump', function (){
            $scope.jump_to_episode({id: 33});
            expect($modalInstance.close).toHaveBeenCalledWith('cancel');
            expect($location.path.calls.count()).toBe(0);
        });

    });

    describe('cancel()', function (){
        it('Should close the modal', function () {
            spyOn($modalInstance, 'close');
            $scope.cancel();
            expect($modalInstance.close).toHaveBeenCalledWith('cancel');
        });
    });

});
