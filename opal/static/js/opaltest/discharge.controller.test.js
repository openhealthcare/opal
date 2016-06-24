describe('DischargeEpisodeCtrl', function(){
    "use strict";

    var $scope, $modal, $httpBackend, $window, $rootScope, $controller;
    var Episode;
    var modalInstance, episodeData;
    var episode, tags;

    var mkcontroller;

    var fields = {};
    var records = {
        "default": [
            {
                name: 'demographics',
                single: true,
                fields: [
                    {name: 'first_name', type: 'string'},
                    {name: 'surname', type: 'string'},
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
                patient_id: 1234,
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


        mkcontroller = function(tags){
            $controller('DischargeEpisodeCtrl', {
                $scope: $scope,
                $window: $window,
                $modalInstance: modalInstance,
                episode: episode,
                tags: tags
            });
        }
        mkcontroller(tags)
    });

    describe('Setup', function(){

        it('should have the current and new categories', function() {
            expect($scope.editing.category).toEqual('Discharged');
        });

        it('should set the category if we ar review', function() {
            episode.location[0].category = 'Review';
            mkcontroller();
            expect($scope.editing.category).toEqual('Unfollow');
        });

        it('should handle arbitrary categories', function() {
            episode.location[0].category = 'Dead';
            mkcontroller();
            expect($scope.editing.category).toEqual('Dead');
        });

        it('should set the tags to mine', function() {
            expect($scope.currentTag).toEqual('mine');
        });

        it('should set the tags to tags when they exist', function() {
            mkcontroller({tag: 'infection', subtag: 'tropical'});
            expect($scope.currentTag).toEqual('infection');
            expect($scope.currentSubTag).toEqual('tropical');
        });

        it('should set the discahrge date from the episode if it exists', function() {
            episode.discharge_date = new Date(2000, 0, 1);
            mkcontroller();
            expect($scope.editing.discharge_date).toEqual(new Date(2000, 0, 1))
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
