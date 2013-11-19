describe('controllers', function() {
    var columns, episodeData, optionsData, patientData, Schema, schema, Episode;

    beforeEach(function() {
        module('opal.controllers');
        columns = [
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
        ];

        episodeData = {
            id: 123,
            demographics: [{
                id: 101,
                name: 'John Smith',
                date_of_birth: '1980-07-31'
            }],
            location: [{
                category: 'Inepisode',
                hospital: 'UCH',
                ward: 'T10',
                bed: '15',
                date_of_admission: '2013-08-01',
                tags: {'mine': true, 'tropical': true}
            }],
            diagnosis: [{
                id: 102,
                condition: 'Dengue',
                provisional: true,
            }, {
                id: 103,
                condition: 'Malaria',
                provisional: false,
            }]
        };

        patientData = {
                "active_episode_id": null,
                "demographics": [
                    {
                        "consistency_token": "0beb0d46",
                        "date_of_birth": "1999-12-12",
                        "hospital_number": "",
                        "id": 2,
                        "name": "Mr WAT",
                        "patient_id": 2
                    }
                ],
                "episodes": {
                    "3": {
                        "antimicrobial": [],
                        "demographics": [
                            {
                                "consistency_token": "0beb0d46",
                                "date_of_birth": "1999-12-12",
                                "hospital_number": "",
                                "id": 2,
                                "name": "Mr WAT",
                                "patient_id": 2
                            }
                        ],
                        "diagnosis": [],
                        "general_note": [],
                        "id": 3,
                        "location": [
                            {
                                "bed": "",
                                "category": "Discharged",
                                "consistency_token": "bd4f5db6",
                                "date_of_admission": "2013-11-14",
                                "discharge_date": null,
                                "episode_id": 3,
                                "hospital": "",
                                "id": 3,
                                "tags": {},
                                "ward": ""
                            }
                        ],
                        "microbiology_input": [],
                        "microbiology_test": [
                            {
                                "adenovirus": "",
                                "anti_hbcore_igg": "",
                                "anti_hbcore_igm": "",
                                "anti_hbs": "",
                                "c_difficile_antigen": "",
                                "c_difficile_toxin": "",
                                "cmv": "",
                                "consistency_token": "29429ebf",
                                "cryptosporidium": "",
                                "date_ordered": "2013-11-14",
                                "details": "",
                                "ebna_igg": "",
                                "ebv": "",
                                "entamoeba_histolytica": "",
                                "enterovirus": "",
                                "episode_id": 3,
                                "giardia": "",
                                "hbsag": "",
                                "hsv": "",
                                "hsv_1": "",
                                "hsv_2": "",
                                "id": 1,
                                "igg": "",
                                "igm": "",
                                "influenza_a": "",
                                "influenza_b": "",
                                "metapneumovirus": "",
                                "microscopy": "",
                                "norovirus": "",
                                "organism": "",
                                "parainfluenza": "",
                                "parasitaemia": "",
                                "resistant_antibiotics": "",
                                "result": "pending",
                                "rotavirus": "",
                                "rpr": "",
                                "rsv": "",
                                "sensitive_antibiotics": "",
                                "species": "",
                                "syphilis": "",
                                "test": "Fasciola Serology",
                                "tppa": "",
                                "vca_igg": "",
                                "vca_igm": "",
                                "viral_load": "",
                                "vzv": ""
                            }
                        ],
                        "past_medical_history": [],
                        "todo": [],
                        "travel": []
                    }
                },
                "id": 2
            }

        optionsData = {
            condition: ['Another condition', 'Some condition']
        }

        inject(function($injector) {
            Schema = $injector.get('Schema');
            Episode = $injector.get('Episode');
        });

        schema = new Schema(columns);
    });

    describe('EpisodeListCtrl', function() {
        var $scope, $cookieStore, $controller, $q, $dialog;
        var episodes, controller;

        beforeEach(function() {
            inject(function($injector) {
                $rootScope = $injector.get('$rootScope');
                $scope = $rootScope.$new();
                $cookieStore = $injector.get('$cookieStore');
                $controller = $injector.get('$controller');
                $q = $injector.get('$q');
                $dialog = $injector.get('$dialog');
            });

            episodes = [new Episode(episodeData, schema)];
            options = optionsData;

            controller = $controller('EpisodeListCtrl', {
                $scope: $scope,
                $cookieStore: $cookieStore,
                schema: schema,
                episodes: episodes,
                options: options
            });
        });

        describe('newly-created controller', function() {
            it('should have state "normal"', function() {
                expect($scope.state).toBe('normal');
            });
        });

        describe('adding an episode', function() {
            it('should change stated to "modal"', function() {
                $scope.addEpisode();
                expect($scope.state).toBe('modal');
            });

            it('should set up the hospital number modal', function() {
                var callArgs;

                spyOn($dialog, 'dialog').andCallThrough();

                $scope.addEpisode();

                callArgs = $dialog.dialog.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].templateUrl).toBe('/templates/modals/hospital_number.html/');
                expect(callArgs[0].controller).toBe('HospitalNumberCtrl');
            });

        });

        describe('editing an item', function() {
            it('should select that item', function() {
                $scope.editItem(0, 0, 0);
                expect([$scope.rix, $scope.cix, $scope.iix]).toEqual([0, 0, 0]);
            });

            it('should change state to "modal"', function() {
                $scope.editItem(0, 0, 0);
                expect($scope.state).toBe('modal');
            });

            it('should set up the demographics modal', function() {
                var callArgs;

                spyOn($dialog, 'dialog').andCallThrough();

                $scope.editItem(0, 0, 0);

                callArgs = $dialog.dialog.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].templateUrl).toBe('/templates/modals/demographics.html/');
                expect(callArgs[0].controller).toBe('EditItemCtrl');
            });

            it('should open the demographics modal', function() {
                var modalSpy;

                modalSpy = {open: function() {}};
                spyOn($dialog, 'dialog').andReturn(modalSpy);
                spyOn(modalSpy, 'open').andReturn({then: function() {}});

                $scope.editItem(0, 0, 0);

                expect(modalSpy.open).toHaveBeenCalled();
            });

            it('should change state to "normal" when the modal is closed', function() {
                var deferred, modalSpy;

                deferred = $q.defer();
                modalSpy = {open: function() {}};
                spyOn($dialog, 'dialog').andReturn(modalSpy);
                spyOn(modalSpy, 'open').andReturn(deferred.promise);

                $scope.editItem(0, 0, 0);

                deferred.resolve('save');
                $rootScope.$apply();

                expect($scope.state).toBe('normal');
            });

            it('should add a new item if result is "save-and-add-another"', function() {
                var deferred, modalSpy;

                deferred = $q.defer();
                modalSpy = {open: function() {}};
                spyOn($dialog, 'dialog').andReturn(modalSpy);
                spyOn(modalSpy, 'open').andReturn(deferred.promise);

                $scope.editItem(0, 0, 0);

                spyOn($scope, 'editItem');
                deferred.resolve('save-and-add-another');
                $rootScope.$apply();

                expect($scope.editItem).toHaveBeenCalledWith(0, 0, 1);
            });
        });

        describe('adding an item', function() {
            var iix;

            beforeEach(function() {
                iix = episodeData.diagnosis.length;
            });

            it('should select "Add"', function() {
                $scope.editItem(0, 2, iix);
                expect([$scope.rix, $scope.cix, $scope.iix]).toEqual([0, 2, iix]);
            });

            it('should change state to "modal"', function() {
                $scope.editItem(0, 2, iix);
                expect($scope.state).toBe('modal');
            });

            it('should set up the modal', function() {
                var callArgs;

                spyOn($dialog, 'dialog').andCallThrough();

                $scope.editItem(0, 2, iix);

                callArgs = $dialog.dialog.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].templateUrl).toBe('/templates/modals/diagnosis.html/');
                expect(callArgs[0].controller).toBe('EditItemCtrl');
                expect(callArgs[0].resolve.item().id).toBeUndefined();
            });
        });

        describe('deleting an item', function() {
            it('should do nothing if item is singleton', function() {
                $scope.deleteItem(0, 0, 0);
                expect($scope.state).toBe('normal');
            });

            it('should do nothing if item is new item', function() {
                $scope.deleteItem(0, 2, 2);
                expect($scope.state).toBe('normal');
            });

            it('should change state to "modal"', function() {
                $scope.deleteItem(0, 2, 1);
                expect($scope.state).toBe('modal');
            });
        });
    });



    describe('SearchCtrl', function (){
        var $scope, $http, $location, $dialog;
        var schema, options;

        beforeEach(function(){
            inject(function($injector){
                $rootScope = $injector.get('$rootScope');
                $scope = $rootScope.$new();
                $controller = $injector.get('$controller');
                $dialog = $injector.get('$dialog');
            });

            options = optionsData

            controller = $controller('SearchCtrl', {
                $scope: $scope,
                $dialog: $dialog,
                schema: schema,
                options: options,
            });

        });


        describe('get relevant episode id', function (){
            it('Should default to the active id', function () {
                var myPatient = _.clone(patientData);
                myPatient.active_episode_id = '3001';
                expect($scope.getEpisodeID(myPatient)).toBe('3001')
            });

            it('Should use the frist episode if we are inactive', function () {
                expect($scope.getEpisodeID(patientData)).toBe('3')
            });
        });

    });

});
