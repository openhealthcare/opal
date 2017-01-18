describe('PatientAccessLogCtrl', function() {
    "use strict";

    var $httpBackend, $rootScope, $scope, $controller;
    var controller;

    beforeEach(module('opal.controllers'));

    beforeEach(function(){
        module('opal');

        inject(function($injector){
            $rootScope   = $injector.get('$rootScope');
            $scope       = $rootScope.$new();
            $controller  = $injector.get('$controller');
            $httpBackend = $injector.get('$httpBackend');
        });
    });


    describe('Initialization', function() {
        it('should set the access log', function() {
            $httpBackend.expectGET('/api/v0.1/patientrecordaccess/12/').respond({the: 'data'})
            controller = $controller('PatientRecordAccessLogCtrl', {
                $scope : $scope,
                patient: {id: 12}
            });
            $rootScope.$apply();
            $httpBackend.flush();
            expect($scope.access_log).toEqual({the: 'data'})
        });
    });

});
