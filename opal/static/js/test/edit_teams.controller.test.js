describe('EditTeamsCtrl', function(){
    "use strict";

    var $scope, $rootScope, $httpBackend, $window, $modal, $controller;
    var Episode;
    var modalInstance;
    var episode
    var options = {
        tag_display: {
            tropical: 'Tropical',
            virology: 'Virology'
        },
        tag_direct_add: ['tropical', 'virology']
    };
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


    var episodeData = {
        date_of_admission: '',
        tagging: [{
          tropical: true,
        }],
        demographics: [
            {
                patient_id: 1234,
                name: 'Jane doe'
            }
        ],
        location: [
            {
                category: 'Inpatient'
            }
        ]
    };


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
        $rootScope.fields = fields;
        episode = new Episode(episodeData);

        episode.tagging = [
                {
                    save: function(a){
                        return {then: function(fn) { fn(); }}
                    },
                    makeCopy: function(){
                      return {tropical: true};
                    }
                }
        ];

        $controller('EditTeamsCtrl', {
            $scope: $scope,
            $window: $window,
            $modalInstance: modalInstance,
            episode: episode
        });
    });

    describe('Setup', function() {

        it('should have an editing object', function() {
            expect($scope.editing).toEqual({tagging: {tropical: true}});
        });

        it('should not set an empty object if there are no tags', function(){
          episode.tagging = [];
          $controller('EditTeamsCtrl', {
              $scope: $scope,
              $window: $window,
              $modalInstance: modalInstance,
              episode: episode
          });
            expect($scope.editing).toEqual({tagging: {}});
        });

        it('should fetch the options', function() {
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            $rootScope.$apply();
            $httpBackend.flush();
        });
    });

    describe('save()', function() {

        it('should save', function() {
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
            spyOn(modalInstance, 'close');
            $scope.save('close');
            $rootScope.$apply();
            $httpBackend.flush();
            expect(modalInstance.close).toHaveBeenCalledWith('close');
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
