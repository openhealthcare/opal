describe('AddEpisodeCtrl', function (){
    "use strict";

    var $scope, $httpBackend, $rootScope;
    var opalTestHelper;
    var modalInstance;

    var referencedata = {
        dogs: ['Poodle', 'Dalmation'],
        hats: ['Bowler', 'Top', 'Sun']
    };

    referencedata.toLookuplists = function(){
        return { dog_list: referencedata.dogs, hats_list: referencedata.hats };
    };

    beforeEach(function(){
        module('opal');
        module('opal.test');

        var $controller, $modal;
        $scope = {};

        inject(function($injector){
            $controller  = $injector.get('$controller');
            $modal       = $injector.get('$modal');
            $httpBackend = $injector.get('$httpBackend');
            $rootScope   = $injector.get('$rootScope');
            opalTestHelper = $injector.get('opalTestHelper');
        });
        $rootScope.fields = opalTestHelper.getRecordLoaderData();

        modalInstance = $modal.open({template: 'Notatemplate'});
        $scope = $rootScope.$new();

        var controller = $controller('AddEpisodeCtrl', {
            $scope        : $scope,
            $modalInstance: modalInstance,
            referencedata : referencedata,
            demographics  : {},
            tags          : {tag: 'id', subtag: 'id_inpatients'}
        });
    });

    describe('save()', function(){
        it('should save', function(){
            var expected = {
              "tagging":{"id":true,"id_inpatients":true},
              "location":{},
              "demographics":{"date_of_birth":"22/01/1970"},
              "start": "22/01/2000"
            };
            $httpBackend.expectPOST('/api/v0.1/episode/', expected).respond({demographics:[{patient_id: 1}]});
            $scope.editing.start = new Date(2000, 0, 22);
            $scope.editing.demographics.date_of_birth = new Date(1970, 0, 22);
            $scope.save();
            $httpBackend.flush();
        });

    });

    describe('cancel()', function(){
        it('should close with null', function(){
            spyOn(modalInstance, 'close');
            $scope.cancel();
            expect(modalInstance.close).toHaveBeenCalledWith(null);
        });
    });


});
