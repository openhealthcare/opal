describe('controllers', function() {
    var columns, fields, episodeData, optionsData, profileData, patientData, Schema, schema, Episode, Item;
    var profile;

    beforeEach(function() {
        module('opal.controllers');
        columns = {
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
            ]
        };
        fields = {}
        _.each(columns.default, function(c){fields[c.name] = c});

        episodeData = {
            id: 123,
            active: true,
            prev_episodes: [],
            next_episodes: [],
            demographics: [{
                id: 101,
                name: 'John Smith',
                date_of_birth: '1980-07-31'
            }],
            tagging: [{'mine': true, 'tropical': true}],
            location: [{
                category: 'Inepisode',
                hospital: 'UCH',
                ward: 'T10',
                bed: '15',
                date_of_admission: '2013-08-01',
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
                    "tagging": {},
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
            condition: ['Another condition', 'Some condition'],
            tag_hierarchy :{'tropical': []}
        }

        injector = angular.injector(['opal.services'])
        Schema   = injector.get('Schema');
        Episode  = injector.get('Episode');
        Item     = injector.get('Item')

        schema = new Schema(columns.default);
        
        profile = {
            readonly   : false,
            can_extract: true,
            can_see_pid: function(){return true; }
        };
    });

    describe('EpisodeListCtrl', function() {
        var $scope, $cookieStore, $controller, $q, $dialog;
        var $location, $routeParams, $http;
        var Flow;
        var episodes, controller;

        beforeEach(function() {
            inject(function($injector) {
                $rootScope   = $injector.get('$rootScope');
                $scope       = $rootScope.$new();
                $cookieStore = $injector.get('$cookieStore');
                $controller  = $injector.get('$controller');
                $q           = $injector.get('$q');
                $modal       = $injector.get('$modal');
                $http        = $injector.get('$http');
                $routeParams = $injector.get('$routeParams');
                $location    = $injector.get('$location');
            });

            episodes = {123: new Episode(episodeData, schema)};
            options = optionsData;
            $routeParams.tag = 'tropical';
            Flow = jasmine.createSpy('Flow').andCallFake(function(){return {then: function(){}}});
            
            $rootScope.fields = fields


            controller = $controller('EpisodeListCtrl', {
                $rootScope    : $rootScope,
                $scope        : $scope,
                $q            : $q,
                $http         : $http,
                $cookieStore  : $cookieStore,
                $location     : $location,
                $routeParams  : $routeParams,
                Flow          : Flow,
                schema        : schema,
                episodes      : episodes,
                profile       : profile,
                options       : options,
                viewDischarged: false
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

            it('should call the enter flow', function() {
                $scope.addEpisode();
                expect(Flow).toHaveBeenCalledWith(
                    'enter', schema, options, {
                        current_tags: {
                            tag   : 'tropical',
                            subtag: 'all'
                        }
                    }
                )
            });

            describe('for a readonly user', function(){
                beforeEach(function(){
                    profile.readonly = true;
                });

                it('should return null', function(){
                    expect($scope.addEpisode()).toBe(null);
                });
            });

        });

        describe('discharging an episode', function(){
            var mockEvent;

            beforeEach(function(){
                mockEvent = {preventDefault: function(){}};
            });

            it('should prevent the link from continuing', function(){
                spyOn(mockEvent, 'preventDefault');
                $scope.dischargeEpisode(0, mockEvent)
            })

            it('should call the exit flow', function(){
                $scope.dischargeEpisode(0, mockEvent);
                expect(Flow).toHaveBeenCalledWith(
                    'exit', schema, options, 
                    {
                        current_tags: {
                            tag: 'tropical', 
                            subtag: 'all'
                        },
                        episode: episodes[123]

                    }
                );
            });

            describe('for a readonly user', function(){
                beforeEach(function(){
                    profile.readonly = true;
                });

                it('should return null', function(){
                    expect($scope.dischargeEpisode(0,  mockEvent)).toBe(null);
                });
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

                spyOn($modal, 'open').andCallThrough();

                $scope.editItem(0, 0, 0);

                callArgs = $modal.open.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].templateUrl).toBe('/templates/modals/demographics.html/tropical/all');
                expect(callArgs[0].controller).toBe('EditItemCtrl');
            });

            it('should open the demographics modal', function() {
                var modalSpy;

                modalSpy = {open: function() {}};
                spyOn($modal, 'open').andReturn({result:  {then: function() {}}});

                $scope.editItem(0, 0, 0);

                expect($modal.open).toHaveBeenCalled();
            });

            it('should change state to "normal" when the modal is closed', function() {
                var deferred;

                deferred = $q.defer();
                spyOn($modal, 'open').andReturn({result: deferred.promise});

                $scope.editItem(0, 0, 0);

                deferred.resolve('save');
                $rootScope.$apply();

                expect($scope.state).toBe('normal');
            });


            describe('for a readonly user', function(){
                beforeEach(function(){
                    profile.readonly = true;
                });

                it('should return null', function(){
                    expect($scope.editItem(0,  0, 0)).toBe(null);
                });
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

                spyOn($modal, 'open').andCallThrough();

                $scope.editItem(0, 2, iix);

                callArgs = $modal.open.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].templateUrl).toBe('/templates/modals/diagnosis.html/tropical/all');
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

            describe('for a readonly user', function(){
                beforeEach(function(){
                    profile.readonly = true;
                });

                it('should return null', function(){
                    expect($scope.deleteItem(0, 0, 0)).toBe(null);
                });
            });

        });
    });

    describe('EpisodeDetailCtrl', function(){
        var $scope, $cookieStore, $modal;
        var Flow;
        var episode;

        beforeEach(function(){
            inject(function($injector){
                $rootScope   = $injector.get('$rootScope');
                $scope       = $rootScope.$new();
                $q           = $injector.get('$q');
                $controller  = $injector.get('$controller');
                $cookieStore = $injector.get('$cookieStore');
                $modal       = $injector.get('$modal');
            });

            episode = new Episode(episodeData, schema);
            Flow = jasmine.createSpy('Flow').andCallFake(function(){return {then: function(){}}});

            controller = $controller('EpisodeDetailCtrl', {
                $scope      : $scope,
                $modal      : $modal,
                $cookieStore: $cookieStore,
                Flow        : Flow,
                schema      : schema,
                episode     : episode,
                options     : optionsData,
                profile     : profile
            });
        });

        describe('initialization', function(){
            it('should set up state', function(){
                expect($scope.episode).toEqual(episode);
            });
        });

        describe('selecting an item', function(){
            it('should select the item', function(){
                $scope.selectItem(1, 34);
                expect($scope.cix).toBe(1);
                expect($scope.iix).toBe(34);
            });
        })

        describe('editing an item', function(){
            it('should open the EditItemCtrl', function(){
                var deferred, callArgs;

                deferred = $q.defer();
                spyOn($modal, 'open').andReturn({result: deferred.promise});

                $scope.editItem(0, 0);

                callArgs = $modal.open.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].controller).toBe('EditItemCtrl');
            });

            describe('for a readonly user', function(){
                beforeEach(function(){
                    profile.readonly = true;
                });

                it('should return null', function(){
                    expect($scope.editItem(0, 0)).toBe(null);
                });
            });

        });

        describe('deleting an item', function(){
            it('should open the DeleteItemConfirmationCtrl', function(){
                var deferred, callArgs;

                deferred = $q.defer();
                spyOn($modal, 'open').andReturn({result: deferred.promise});

                $scope.deleteItem(2, 0);

                callArgs = $modal.open.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].controller).toBe('DeleteItemConfirmationCtrl');
            });

            describe('for a readonly user', function(){
                beforeEach(function(){
                    profile.readonly = true;
                });

                it('should return null', function(){
                    expect($scope.deleteItem(0, 0)).toBe(null);
                });
            });

        });

        describe('discharging an episode', function(){
            var mockEvent;

            beforeEach(function(){
                mockEvent = {preventDefault: function(){}};
            });

            it('should call the exit flow', function(){
                $scope.dischargeEpisode(mockEvent);
                expect(Flow).toHaveBeenCalledWith(
                    'exit', schema, options, 
                    {
                        current_tags: {
                            tag   : undefined, 
                            subtag: undefined
                        },
                        episode: episode

                    }
                );
            });

            describe('for a readonly user', function(){
                beforeEach(function(){
                    profile.readonly = true;
                });

                it('should return null', function(){
                    expect($scope.dischargeEpisode(mockEvent)).toBe(null);
                });
            })

        });

    });

    // TODO: Actual Tests Here Please
    describe('SearchCtrl', function(){

    });

    describe('ReopenEpisodeCtrl', function (){
        var $scope,  $timeout;
        var dialog, patient, tag;

        beforeEach(function(){
            inject(function($injector){
                $rootScope   = $injector.get('$rootScope');
                $scope       = $rootScope.$new();
                $controller  = $injector.get('$controller');
                $modal       = $injector.get('$modal');
                $timeout     = $injector.get('$timeout');
            });

            modalInstance = $modal.open({template: 'notarealtemplate!'});
            patient = patientData;
            tag: 'mine';

            controller = $controller('ReopenEpisodeCtrl', {
                $scope  : $scope,
                $timeout: $timeout,
                $modalInstance  : modalInstance,
                patient : patient,
                tag     : tag,
            });

        });

        describe('initialization', function(){
            it('should set up state', function(){
                expect($scope.episodes).toEqual(_.values(patientData.episodes));
                expect($scope.model.episodeId).toEqual('None');
            });
        });

        describe('Sorting episodes', function (){
            it('Should deal with unset admission dates', function () {
                expect($scope.sortEpisodes({}, {})).toEqual(-1)
            });

            it('Should know which episode was frist', function () {
                var e1 = {date_of_admission: new Date(2012, 10, 24)};
                var e2 = {};
                expect($scope.sortEpisodes(e1, e2)).toEqual(1)
            });

            it('Should know which episode was frist', function () {
                var e1 = {date_of_admission: new Date(2012, 10, 24)};
                var e2 = {date_of_admission: new Date(2013, 10, 24)};
                expect($scope.sortEpisodes(e1, e2)).toEqual(-1)
            });

            it('Should know which episode was frist', function () {
                var e1 = {date_of_admission: new Date(2013, 10, 24)};
                var e2 = {date_of_admission: new Date(2012, 10, 24)};
                expect($scope.sortEpisodes(e1, e2)).toEqual(1)
            });

            it('Should know when episodes are sorted the same', function () {
                var e1 = {date_of_admission: new Date(2012, 10, 24)};
                var e2 = {date_of_admission: new Date(2012, 10, 24)};
                expect($scope.sortEpisodes(e1, e2)).toEqual(0)
            });
        });

        describe('Opening a new episode', function(){
            it('should close with the appropriate value', function(){
                spyOn(modalInstance, 'close');
                $scope.openNew();
                expect(modalInstance.close).toHaveBeenCalledWith('open-new');
            });
        });

    });

    describe('EditItemCtrl', function (){
        var $scope, $cookieStore, $timeout;
        var dialog, item, options, episode, ngProgressLite;

        beforeEach(function(){
            inject(function($injector){
                $httpBackend = $injector.get('$httpBackend');

                $rootScope   = $injector.get('$rootScope');
                $scope       = $rootScope.$new();
                $controller  = $injector.get('$controller');
                $cookieStore = $injector.get('$cookieStore');
                $modal       = $injector.get('$modal');
                $timeout     = $injector.get('$timeout');
                ngProgressLite   = $injector.get('ngProgressLite');
            });

            options = optionsData;
            profile = profileData;
            episode = new Episode(episodeData, schema);
            item    = new Item(
                {columnName: 'diagnosis'},
                episode,
                schema.columns[0]
            )
            dialog = $modal.open({template: 'notarealtemplate!'})

            controller = $controller('EditItemCtrl', {
                $scope      : $scope,
                $cookieStore: $cookieStore,
                $timeout    : $timeout,
                $modalInstance: dialog,
                item        : item,
                options     : options,
                profile     : profile,
                episode     : episode,
                ngProgressLite  : ngProgressLite,
            });

        });

        describe('newly-created-controller', function (){
            it('Should have subtag "all"', function () {
                expect($scope.currentSubTag).toBe('all')
                expect($scope.columnName).toBe('diagnosis');
            });
        });


        describe('Saving items', function (){

            it('Should save the current item', function () {
                var callArgs;

                spyOn(item, 'save').andCallThrough();

                $scope.save('save');

                callArgs = item.save.mostRecentCall.args;

                expect(callArgs.length).toBe(1);
                expect(callArgs[0]).toBe($scope.editing)
            });

        });

    });


    describe('SearchCtrl', function (){
        var $scope, $http, $location, $dialog;
        var schema, options;

        beforeEach(function(){
            inject(function($injector){
                $rootScope   = $injector.get('$rootScope');
                $scope       = $rootScope.$new();
                $controller  = $injector.get('$controller');
                $timeout     = $injector.get('$timeout');
                $modal       = $injector.get('$modal');
            });

            options = optionsData;

            controller = $controller('SearchCtrl', {
                $scope:   $scope,
                $dialog:  $dialog,
                $timeout: $timeout,
                schema:   schema,
                options:  options,
                profile:  profile
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

    describe('HospitalNumberCtrl', function(){
        var $scope, $timeout, $modal, $modalInstance, $http, $q;
        var tags;

        beforeEach(function(){
            inject(function($injector){
                $httpBackend = $injector.get('$httpBackend');
                $rootScope   = $injector.get('$rootScope');
                $scope       = $rootScope.$new();
                $q           = $injector.get('$q');
                $controller  = $injector.get('$controller');
                $timeout     = $injector.get('$timeout');
                $modal       = $injector.get('$modal');
            });

            options = optionsData;
            modalInstance = $modal.open({template: 'notatemplate'});

            controller = $controller('HospitalNumberCtrl', {
                $scope:         $scope,
                $timeout:       $timeout,
                $modal:         $modal,
                $modalInstance: modalInstance,
                schema:         schema,
                options:        options,
                tags:           {tag: 'mine', subtag: 'all'},
                hospital_number: null
            });
        });

        describe('newly created controller', function(){

            it('should have set up the model', function(){
                expect($scope.model).toEqual({});
            });

        });

        describe('new patient', function(){

            it('should open AddEpisodeCtrl', function(){
                var deferred, callArgs;

                deferred = $q.defer();

                spyOn($modal, 'open').andReturn({result: deferred.promise});
                $scope.newPatient({patients: [], hospitalNumber: 123})

                callArgs = $modal.open.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].controller).toBe('AddEpisodeCtrl');
            });

            it('should close the modal with a new patient', function(){
                var deferred;

                deferred = $q.defer();

                spyOn($modal, 'open').andReturn({result: deferred.promise});
                spyOn(modalInstance, 'close');
                $scope.newPatient({patients: [], hospitalNumber: 123});

                deferred.resolve(patientData);

                $rootScope.$apply();
                expect(modalInstance.close).toHaveBeenCalledWith(patientData);
            })
        });

        describe('new for patient', function(){
            
            it('should call through if there is an active discharged episode.', function(){
                spyOn($scope, 'newForPatientWithActiveEpisode');

                patientData.active_episode_id = 3;

                deferred = $q.defer();
                spyOn($modal, 'open').andReturn({result: deferred.promise});

                $scope.newForPatient(patientData);

                callArgs = $modal.open.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].controller).toBe('ReopenEpisodeCtrl');
                expect(callArgs[0].resolve.tag()).toBe('mine');
            });
            
            it('should call through if there is an active episode.', function(){
                spyOn($scope, 'newForPatientWithActiveEpisode');
                patientData.active_episode_id = 3;
                patientData.episodes[3].location[0].category = 'Inpatient'
                
                $scope.newForPatient(patientData);
                expect($scope.newForPatientWithActiveEpisode)
                    .toHaveBeenCalledWith(patientData);
            });

            it('should call ??? if there is an active discharged episode.', function(){
                // TODO
            });

            it('should call through if there are no active episodes', function(){
                var patient;

                spyOn($scope, 'addForPatient');
                patient = angular.copy(patientData)
                patient.episodes = {};

                $scope.newForPatient(patient);
                expect($scope.addForPatient).toHaveBeenCalledWith(patient);
            });

            it('should offer to reopen episodes', function(){
                var deferred, callArgs;

                deferred = $q.defer();
                spyOn($modal, 'open').andReturn({result: deferred.promise});

                $scope.newForPatient(patientData);

                callArgs = $modal.open.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].controller).toBe('ReopenEpisodeCtrl');
                expect(callArgs[0].resolve.tag()).toBe('mine');
            });

            it('should open a new episode', function(){
                var deferred;

                deferred = $q.defer();
                spyOn($modal, 'open').andReturn({result: deferred.promise});
                spyOn($scope, 'addForPatient');

                $scope.newForPatient(patientData);
                deferred.resolve('open-new');

                $rootScope.$apply();

                expect($scope.addForPatient).toHaveBeenCalledWith(patientData);
            });

            it('should pass through the reopened episode', function(){
                var deferred;

                deferred = $q.defer();
                spyOn($modal, 'open').andReturn({result: deferred.promise});
                spyOn(modalInstance, 'close');

                $scope.newForPatient(patientData);
                deferred.resolve(patientData.episodes[3]);

                $rootScope.$apply();

                expect(modalInstance.close).toHaveBeenCalledWith(
                    patientData.episodes[3]);
            });

        });

        describe('adding for a patient', function(){

            it('should open AddEpisodeCtrl', function(){
                var deferred, callArgs;

                deferred = $q.defer();

                spyOn($modal, 'open').andReturn({result: deferred.promise});

                $scope.addForPatient(patientData);

                callArgs = $modal.open.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].controller).toBe('AddEpisodeCtrl');
            });

            it('should pass through demographics', function(){
                var deferred, callArgs;

                deferred = $q.defer();

                spyOn($modal, 'open').andReturn({result: deferred.promise});

                $scope.addForPatient(patientData);

                callArgs = $modal.open.mostRecentCall.args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].resolve.demographics())
                    .toEqual(patientData.demographics[0]);
            });

            it('should close the dialog with the new episode', function(){
                var deferred, episode, callArgs;

                deferred = $q.defer();
                episode = new Episode({id: 3}, schema);

                spyOn($modal, 'open').andReturn({result: deferred.promise});
                spyOn(modalInstance, 'close');

                $scope.addForPatient(patientData);

                deferred.resolve(episode)
                $rootScope.$apply();

                callArgs = modalInstance.close.mostRecentCall.args;
                expect(callArgs[0].makeCopy()).toEqual(episode.makeCopy());
            });

        })

        describe('cancelling the modal', function(){
            it('should close with null', function(){
                spyOn(modalInstance, 'close');
                $scope.cancel()
                expect(modalInstance.close).toHaveBeenCalledWith(null)
            })
        });

    });

    describe('AddEpisodeCtrl', function (){
        var $scope

        beforeEach(function(){
            var $controller, $modal
            $scope = {};

            inject(function($injector){
                $controller = $injector.get('$controller');
                $modal = $injector.get('$modal');
            });

            dialog = $modal.open({template: 'Notatemplate'});
            var controller = $controller('AddEpisodeCtrl', {
                $scope: $scope,
                $modalInstance: dialog,
                schema: schema,
                options: optionsData,
                demographics: {}
            });


        });

        describe('Adding an episode', function (){

            it('Should set up the initial editing situation', function () {
                expect($scope.editing.tagging).toEqual([{mine: true}]);
            });

        });

    });

    describe('DeleteItemConfirmationCtrl', function(){
        var $scope, $timeout;
        var item;

        beforeEach(function(){
            inject(function($injector){
                $rootScope  = $injector.get('$rootScope');
                $scope      = $rootScope.$new();
                $controller = $injector.get('$controller');
                $timeout    = $injector.get('$timeout');
                $modal      = $injector.get('$modal');
                $q          = $injector.get('$q')
            });

            $modalInstance = $modal.open({template: 'notarealtemplate'});
            item = { destroy: function(){} };

            controller = $controller('DeleteItemConfirmationCtrl', {
                $scope        : $scope,
                $timeout      : $timeout,
                $modalInstance: $modalInstance,
                item          : item
            });
        });

        describe('deleting', function(){
            it('should call destroy on the modal', function(){
                var deferred;

                deferred = $q.defer();
                spyOn(item, 'destroy').andReturn(deferred.promise);
                spyOn($modalInstance, 'close');

                $scope.destroy();
                deferred.resolve();
                $rootScope.$apply();

                expect(item.destroy).toHaveBeenCalledWith();
                expect($modalInstance.close).toHaveBeenCalledWith('deleted');
            })
        });

        describe('cancelling', function(){
            it('should close the modal', function(){
                spyOn($modalInstance, 'close');
                $scope.cancel();
                expect($modalInstance.close).toHaveBeenCalledWith('cancel')
            })
        });
    });

    describe('ExtractCtrl', function(){
        beforeEach(function(){
            
            inject(function($injector){
                $httpBackend = $injector.get('$httpBackend');
            });

            var $injector = angular.injector(['ng', 'opal.controllers'])
            $scope   = $injector.get('$rootScope');
            // $scope       = $rootScope.$new();
            $controller  = $injector.get('$controller');
            $window      = $injector.get('$window');

            Schema = $injector.get('Schema');
            Episode = $injector.get('Episode');
            Item = $injector.get('Item')

        var schema = new Schema(columns.default);

            controller = $controller('ExtractCtrl',  {
                $scope : $scope,
                profile: {},
                options: optionsData,
                filters: [],
                schema : schema
            });
        });

        describe('Initialization', function(){
            it('should set up initial state', function(){
                // expect($scope.columns).toEqual(columns.default);
            });
        });

        describe('Getting searchable fields', function(){
            it('should exclude token fields', function(){
                var col = {fields: [
                    {name: 'consistency_token', type: 'token'},
                    {name: 'hospital', type: 'string'},
                ]}
                expect($scope.searchableFields(col)).toEqual(['Hospital'])
            });
            it('should capitalze the field names', function(){
                var col = {fields: [
                    {name: 'hospital_number', type: 'string'},
                    {name: 'hospital', type: 'string'},
                ]}
                expect($scope.searchableFields(col)).toEqual(['Hospital Number',
                                                              'Hospital']);
            });
        });

        describe('Search', function(){
            it('should ask the server for results', function(){
                $httpBackend.when('POST', "/search/extract/").respond(patientData.episodes);
                $scope.search();
            });
        });

    });

});
