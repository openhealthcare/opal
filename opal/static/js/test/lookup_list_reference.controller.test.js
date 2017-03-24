describe('LookupListReferenceCtrl', function() {
    "use strict";

    var $controller, $scope;
    var modalInstance = {dismiss: function(){}};
    var lookuplist, lookuplist_name;

    beforeEach(module('opal.controllers'));

    beforeEach(inject(function($injector){
        lookuplist_name = 'thelookuplist';
        lookuplist = ['An', 'Entry', 'In', 'A', 'List'];
        $controller = $injector.get('$controller');
        var $rootScope = $injector.get('$rootScope');
        $scope = $rootScope.$new();
        $controller('LookupListReferenceCtrl', {
            $scope: $scope,
            $modalInstance: modalInstance,
            lookuplist_name: lookuplist_name,
            lookuplist: lookuplist
        });

    }));

    describe('$scope', function() {

        it('should have variables set', function() {
            expect($scope.lookuplist).toEqual(lookuplist);
            expect($scope.lookuplist_name).toEqual(lookuplist_name);
        });

    });

    describe('cancel()', function(){

        it('should close with null', function(){
            spyOn(modalInstance, 'dismiss');
            $scope.cancel();
            expect(modalInstance.dismiss).toHaveBeenCalledWith('cancel');
        });

    })

});
1
