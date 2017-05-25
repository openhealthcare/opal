describe('DischargeEpisodeCtrl', function(){
    "use strict";

    var $scope, $modal, $httpBackend, $window, $rootScope, $controller;
    var Episode;
    var modalInstance, episodeData, episode, tags, fields, records;
    var mkcontroller;

    fields = {};
    records = {
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


    beforeEach(function(){
        episodeData = {
            id: '555',
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
        };

        module('opal.controllers');

        inject(function($injector){
            $rootScope   = $injector.get('$rootScope');
            $window      = $injector.get('$window');
            $controller  = $injector.get('$controller');
            $httpBackend = $injector.get('$httpBackend');
            $modal       = $injector.get('$modal');
            Episode      = $injector.get('Episode');
        });

        modalInstance = $modal.open({template: 'notatemplate'});
        tags = {};
        $rootScope.fields = fields;
        episode = new Episode(episodeData)

        mkcontroller = function(tags, _episode){
          _episode = _episode || episode;
          $scope = $rootScope.$new();

          $controller('DischargeEpisodeCtrl', {
              $scope: $scope,
              $window: $window,
              $modalInstance: modalInstance,
              episode: _episode,
              tags: tags
          });
        }
        mkcontroller(tags)
        $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
    });

    describe('Set up the controller', function(){

        afterEach(function(){
            $httpBackend.flush();
        })

        it('should have the current and new categories', function() {
            expect($scope.editing.category).toEqual('Discharged');
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

            $httpBackend.expectPUT('/api/v0.1/tagging/555/').respond({});
            $httpBackend.expectPOST('/api/v0.1/location/').respond({});
            $httpBackend.expectPUT('/api/v0.1/episode/555/').respond(episodeData);
            spyOn(modalInstance, 'close')

            $scope.discharge();

            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingRequest();
            $httpBackend.verifyNoOutstandingExpectation();

            expect(modalInstance.close).toHaveBeenCalledWith('discharged')
        });

        it('should remove the discharge date if category is Unfollow', function() {
            $httpBackend.expectPUT('/api/v0.1/tagging/555/').respond({});
            $httpBackend.expectPOST('/api/v0.1/location/').respond({});

            var expected = {"id":"555","date_of_admission": "","discharge_date": null};
            $httpBackend.expectPUT('/api/v0.1/episode/555/', expected).respond(episodeData);

            var alteredEpisodeData = angular.copy(episodeData);
            alteredEpisodeData.discharge_date = moment();
            mkcontroller(tags, new Episode(alteredEpisodeData));
            $scope.editing.category = "Unfollow";
            $scope.discharge();
            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingRequest();
            $httpBackend.verifyNoOutstandingExpectation();
        });

        it('should use the discharge date from editing if the category is not Unfollow', function() {
            $httpBackend.expectPUT('/api/v0.1/tagging/555/').respond({});
            $httpBackend.expectPOST('/api/v0.1/location/').respond({});
            var alteredEpisodeData = angular.copy(episodeData);
            alteredEpisodeData.discharge_date = moment(new Date(20016, 6, 6));

            var expected = {"id":"555","date_of_admission": "","discharge_date": "06/07/20016"};
            $httpBackend.expectPUT('/api/v0.1/episode/555/', expected).respond(alteredEpisodeData);
            mkcontroller(tags, new Episode(alteredEpisodeData));
            $scope.editing.category = "Followup";
            $scope.discharge();
            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingRequest();
            $httpBackend.verifyNoOutstandingExpectation();
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
