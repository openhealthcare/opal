describe('DischargeEpisodeCtrl', function(){
    "use strict";

    var $scope, $modal, $httpBackend, $window, $rootScope, $controller;
    var Episode;
    var modalInstance, episodeData;
    var episode, tags;

    var fields = {};
    var records = {
        "default": [
            {
                name: 'demographics',
                single: true,
                fields: [
                    {name: 'name', type: 'string'},
                    {name: 'date_of_birth', type: 'date'},
                ]},
            {
                name: 'location',
                single: true,
                fields: [
                    {name: 'category', type: 'string'},
                    {name: 'hospital', type: 'string'},
                    {name: 'ward', type: 'string'},
                    {name: 'bed', type: 'string'},
                    {name: 'date_of_admission', type: 'date'},
                    {name: 'tags', type: 'list'},
                ]},
            {
                name: 'diagnosis',
                single: false,
                fields: [
                    {name: 'condition', type: 'string'},
                    {name: 'provisional', type: 'boolean'},
                ]},
            {
                "name": "tagging",
                "single": true,
                "display_name": "Teams",
                "advanced_searchable": true,
                "fields": [
                    {
                        "type": "boolean",
                        "name": "mine"
                    },
                    {
                        "type": "boolean",
                        "name": "tropical"
                    },
                    {
                        "type": "boolean",
                        "name": "main"
                    },
                    {
                        "type": "boolean",
                        "name": "secondary"
                    }
                ]
            }
        ]
    };


    _.each(records.default, function(c){
        fields[c.name] = c;
    });


    episodeData = {
        date_of_admission: '',
        tagging: [{tropical: true}],
        demographics: [
            {
                name: 'Jane doe'
            }
        ],
        location: [
            {
                category: 'Inpatient'
            }
        ]
    }

    beforeEach(function(){
        module('opal.controllers');

        inject(function($injector){
            $httpBackend = $injector.get('$httpBackend');
            $rootScope   = $injector.get('$rootScope');
            $scope       = $rootScope.$new();
            $window      = $injector.get('$window');
            $controller  = $injector.get('$controller');
            $modal       = $injector.get('$modal');
            Episode      = $injector.get('Episode');
        });

        modalInstance = $modal.open({template: 'notatemplate'});
        tags = {};
        $rootScope.fields = fields;
        episode = new Episode(episodeData)

        $controller('DischargeEpisodeCtrl', {
            $scope: $scope,
            $window: $window,
            $modalInstance: modalInstance,
            episode: episode,
            tags: tags
        })

    });

    describe('Setup', function(){

        it('should have the current and new categories', function() {
            expect($scope.editing.category).toEqual('Discharged');
        });

    });

    describe('discharge()', function() {

        it('should discharge the patient', function() {
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            $scope.discharge();
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
