describe('RootCtrl', function() {
    "use strict";

    var $controller, $scope;

    beforeEach(module('opal.controllers'));

    beforeEach(inject(function($injector){
        $controller = $injector.get('$controller');
        var $rootScope = $injector.get('$rootScope');
        $scope = $rootScope.$new();
        $controller('RootCtrl', {
            $scope: $scope,
        });

    }));

    describe('keydown', function(){
        it('should broadcast', function() {
            spyOn($scope, '$broadcast');
            $scope.keydown('wat');
            expect($scope.$broadcast).toHaveBeenCalledWith('keydown', 'wat');
        });
    });

});
