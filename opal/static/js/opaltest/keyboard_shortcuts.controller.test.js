describe('KeyboardShortcutsCtrl', function() {
    "use strict";

    var $controller, $scope;
    var modalInstance = {dismiss: function(){}};

    beforeEach(module('opal.controllers'));

    beforeEach(inject(function($injector){
        $controller = $injector.get('$controller');
        var $rootScope = $injector.get('$rootScope');
        $scope = $rootScope.$new();
        $controller('KeyBoardShortcutsCtrl', {
            $scope: $scope,
            $modalInstance: modalInstance
        });

    }));

    describe('cancel()', function(){

        it('should close with null', function(){
            spyOn(modalInstance, 'dismiss');
            $scope.cancel();
            expect(modalInstance.dismiss).toHaveBeenCalledWith('cancel');
        });

    })

});
