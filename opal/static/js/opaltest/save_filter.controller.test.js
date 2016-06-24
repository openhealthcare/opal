describe('SaveFilterCtrl', function() {
    var $scope;
    var modalInstance;
    var mock_ng_progress;


    beforeEach(function(){
        module('opal.controllers');

        inject(function($injector){
            $httpBackend = $injector.get('$httpBackend');
            $rootScope   = $injector.get('$rootScope');
            $scope       = $rootScope.$new();
            $controller  = $injector.get('$controller');
        });

        modalInstance = $modal.open({template: 'notatemplate'});
        mock_ng_progress = {

        }

        $controller('SaveFilterCtrl', {
            $scope: $scope,
            $modalInstance: modalInstance,
            params: {}
        })
    });

    describe('save()', function() {

        it('should save()', function() {
            $httpBackend.expectPOST('/search/filters/').respond({})
            spyOn(modalInstance, 'close');
            $scope.save();
            $rootScope.$apply();
            $httpBackend.flush();
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
