describe('AddEpisodeCtrl', function (){
    "use strict";

    var $scope, $httpBackend, $rootScope;
    var Schema
    var modalInstance;
    var fields = {
        'demographics': {
            name: "demographics",
            single: true,
            fields: [
                {name: 'name', type: 'string'},
                {name: 'date_of_birth', type: 'date'},
                {name: 'created', type: 'date_time'},
            ],
        },
        "diagnosis": {
            name: "diagnosis",
            single: false,
            sort: 'date_of_diagnosis',
            fields: [
                {name: 'date_of_diagnosis', type: 'date'},
                {name: 'condition', type: 'string', default: 'flu'},
                {name: 'provisional', type: 'boolean'},
            ]
        }
    };

    var referencedata = {
        dogs: ['Poodle', 'Dalmation'],
        hats: ['Bowler', 'Top', 'Sun']
    };

    referencedata.toLookuplists = function(){
        return { dog_list: referencedata.dogs, hats_list: referencedata.hats };
    };

    beforeEach(function(){
        module('opal');
        var $controller, $modal;
        $scope = {};

        inject(function($injector){
            $controller  = $injector.get('$controller');
            $modal       = $injector.get('$modal');
            $httpBackend = $injector.get('$httpBackend');
            Schema       = $injector.get('Schema');
            $rootScope   = $injector.get('$rootScope');
        });
        $rootScope.fields = fields;

        // var schema = new Schema(columns.default);
        modalInstance = $modal.open({template: 'Notatemplate'});
        $scope = $rootScope.$new();

        var controller = $controller('AddEpisodeCtrl', {
            $scope        : $scope,
            $modalInstance: modalInstance,
            referencedata : referencedata,
            demographics  : {},
            tags          : {tag: 'id', subtag: 'id_inpatients'}
        });

        $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
        $scope.$apply();
        $httpBackend.flush();

    });

    describe('save()', function(){
        it('should save', function(){
            var expected = {
              "tagging":{"id":true,"id_inpatients":true},
              "location":{},
              "demographics":{"date_of_birth":"22/01/1970"},
              "date_of_admission":"22/01/2000"
            };
            $httpBackend.expectPOST('/api/v0.1/episode/', expected).respond({demographics:[{patient_id: 1}]});
            $scope.editing.date_of_admission = new Date(2000, 0, 22);
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
