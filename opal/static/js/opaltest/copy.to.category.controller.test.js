describe('CopyToCategoryCtrl', function(){
    var $scope, $httpBackend, $modal, $rootScope, $window;
    var modalInstance;
    var patient, category;

    beforeEach(function(){
        module('opal.controllers');

        inject(function($injector){
            $httpBackend = $injector.get('$httpBackend');
            $rootScope   = $injector.get('$rootScope');
            $scope       = $rootScope.$new();
            $controller  = $injector.get('$controller');
            $modal       = $injector.get('$modal');
            $window      = $injector.get('$window');
        });

        patient = {};
        category_name = 'newcategory';
        modalInstance = $modal.open({template: 'notatemplate'});

        $controller('CopyToCategoryCtrl', {
            $scope: $scope,
            patient: patient,
            category_name: category_name,
            $modalInstance: modalInstance
        })
    });

    describe('jump_to_episode()', function(){

        it('should go there', function(){
            spyOn($window, 'open');
            $scope.jump_to_episode(12);
            expect($window.open).toHaveBeenCalledWith('#/episode/12', '_blank')
        });

    });

    describe('open_new()', function(){

        it('should close with null', function(){
            spyOn(modalInstance, 'close');
            $scope.open_new();
            expect(modalInstance.close).toHaveBeenCalledWith('open-new');
        });

    })

    describe('import_existing()', function(){

        it('should close the modal', function(){
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            $httpBackend.expectPOST('/episode/2/actions/copyto/newcategory').respond({
                demographics: [{patient_id: 2}]
            });

            spyOn(modalInstance, 'close');
            patient.active_episode_id = 2;
            $scope.import_existing();

            $rootScope.$apply();
            $httpBackend.flush();

            expect(modalInstance.close).toHaveBeenCalled()
        });

    })

    describe('cancel()', function(){

        it('should close with null', function(){
            spyOn(modalInstance, 'close');
            $scope.cancel();
            expect(modalInstance.close).toHaveBeenCalledWith('cancel');
        });

    })

});
