describe('404Ctrl', function() {
    var $controller, $scope;

    beforeEach(module('opal.controllers'));

    beforeEach(inject(function($injector){
        $controller = $injector.get('$controller');
        var $rootScope = $injector.get('$rootScope');
        $scope = $rootScope.$new();

        $controller('404Ctrl', {
            $scope: $scope
        });

    }));

    describe('initialise', function(){

        it('should initialise', function() {
            null;
        });

    });

});
