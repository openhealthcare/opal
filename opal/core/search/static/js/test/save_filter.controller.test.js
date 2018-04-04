describe('SaveFilterCtrl', function() {
    "use strict";

    var $scope, $httpBackend, $controller, $rootScope, $modal, $window;
    var modalInstance, ngProgressLite;


    beforeEach(function(){
        module('opal.controllers');

        inject(function($injector){
            $httpBackend     = $injector.get('$httpBackend');
            $rootScope       = $injector.get('$rootScope');
            $scope           = $rootScope.$new();
            $controller      = $injector.get('$controller');
            $modal           = $injector.get('$modal');
            ngProgressLite   = $injector.get('ngProgressLite');
            $window          = $injector.get('$window');

        });

        modalInstance = $modal.open({template: 'notatemplate'});

        $controller('SaveFilterCtrl', {
            $scope: $scope,
            $modalInstance: modalInstance,
            params: {},
            ngProgressLite: ngProgressLite
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

        it('should kill the progressbar if we error', function() {
            $httpBackend.expectPOST('/search/filters/').respond(500)
            spyOn(ngProgressLite, 'done');
            spyOn($window, 'alert');
            $scope.save();
            $rootScope.$apply();
            $httpBackend.flush();
            expect(ngProgressLite.done).toHaveBeenCalledWith();
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
