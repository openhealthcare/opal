describe('EpisodeListCtrl', function() {
    var episodeData, optionsData, profileData, patientData, Schema;
    var schema, Episode, Item;
    var profile;
    var $scope, $cookieStore, $controller, $q, $dialog;
    var $location, $routeParams, $http;
    var Flow, flow_promise;
    var episodes, controller;
    var $modal;

    var fields = {};
    var columns = {
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

    _.each(columns.default, function(c){
        fields[c.name] = c;
    });

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
    };

    optionsData = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    };

    profile = {
        can_edit: function(x){
          return true;
        },
        readonly   : false,
        can_extract: true,
        can_see_pid: function(){return true; }
    };


    beforeEach(module('opal.controllers'));

    beforeEach(inject(function($injector){
        Schema   = $injector.get('Schema');
        Episode  = $injector.get('Episode');
        Item     = $injector.get('Item');
        $rootScope   = $injector.get('$rootScope');
        $scope       = $rootScope.$new();
        $cookieStore = $injector.get('$cookieStore');
        $controller  = $injector.get('$controller');
        $q           = $injector.get('$q');
        $modal       = $injector.get('$modal');
        $http        = $injector.get('$http');
        $routeParams = $injector.get('$routeParams');
        $location    = $injector.get('$location');

        schema = new Schema(columns.default);
        episodes = {123: new Episode(episodeData)};
        options = optionsData;
        $routeParams.tag = 'tropical';
        flow_promise = {then: function(){}};
        Flow = jasmine.createSpy('Flow').and.callFake(function(){return flow_promise});
        $rootScope.fields = fields;

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
    }));


    describe('newly-created controller', function() {
        it('should have state "normal"', function() {
            expect($rootScope.state).toBe('normal');
        });
    });

    describe('adding an episode', function() {
        it('should change stated to "modal"', function() {
            $scope.addEpisode();
            expect($rootScope.state).toBe('modal');
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
            );
        });

        describe('for a readonly user', function(){
            beforeEach(function(){
                profile.readonly = true;
            });

            it('should return null', function(){
                expect($scope.addEpisode()).toBe(null);
            });

            afterEach(function(){
                profile.readonly = false;
            });
        });
    });

    describe('discharging an episode', function(){
        describe('_post_discharge()', function (){

            beforeEach(function(){
                $rootScope.state = 'modal'
            });

            it('Should set the $scope.state', function () {
                $scope._post_discharge();
                expect($rootScope.state).toBe('normal');
            });

            it('Should re-set the visible episodes', function () {
                spyOn($scope, 'getVisibleEpisodes').and.callThrough();
                $scope._post_discharge('discharged');
                expect($scope.getVisibleEpisodes).toHaveBeenCalledWith();
            });

            it('Should re-set the focus to 0', function () {
                spyOn($scope, 'selectItem');
                $scope._post_discharge('discharged');
                expect($scope.selectItem).toHaveBeenCalledWith(0, 0, 0);
            });
        });

        it('should call the exit flow', function(){
            $scope.dischargeEpisode(0);
            expect(Flow).toHaveBeenCalled()
        });

        describe('for a readonly user', function(){
            beforeEach(function(){
                profile.readonly = true;
            });

            it('should return null', function(){
                expect($scope.dischargeEpisode(0)).toBe(null);
            });

            afterEach(function(){
                profile.readonly = false;
            });
        });

        describe('when Flow() returns a deferred', function (){
                it('Should wait for the deferred', function () {
                    var returned_deferred = {then: function(fn){fn()}}
                    spyOn($scope, '_post_discharge');
                    spyOn(returned_deferred, 'then').and.callThrough();
                    spyOn(flow_promise, 'then').and.callFake(function(fn){ fn(returned_deferred);})

                    $scope.dischargeEpisode(0);

                    expect(flow_promise.then).toHaveBeenCalled();
                    expect(returned_deferred.then).toHaveBeenCalled();
                    expect($scope._post_discharge).toHaveBeenCalled();
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
                expect($rootScope.state).toBe('modal');
            });

            it('should set up the demographics modal', function() {
                var callArgs;

                spyOn($modal, 'open').and.callThrough();
                $scope.editItem(0, 0, 0);

                callArgs = $modal.open.calls.mostRecent().args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].templateUrl).toBe('/templates/modals/demographics.html/tropical/all');
                expect(callArgs[0].controller).toBe('EditItemCtrl');
            });

            it('should open the demographics modal', function() {
                var modalSpy;

                modalSpy = {open: function() {}};
                spyOn($modal, 'open').and.returnValue({result:  {then: function() {}}});

                $scope.editItem(0, 0, 0);

                expect($modal.open).toHaveBeenCalled();
            });

            it('should change state to "normal" when the modal is closed', function() {
                var deferred;

                deferred = $q.defer();
                spyOn($modal, 'open').and.returnValue({result: deferred.promise});

                $scope.editItem(0, 0, 0);

                deferred.resolve('save');
                $rootScope.$apply();

                expect($rootScope.state).toBe('normal');
            });


            describe('for a readonly user', function(){
                beforeEach(function(){
                    profile.readonly = true;
                });

                it('should return null', function(){
                    expect($scope.editItem(0,  0, 0)).toBe(null);
                });

                afterEach(function(){
                    profile.readonly = false;
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
                expect($rootScope.state).toBe('modal');
            });

            it('should set up the modal', function() {
                var callArgs;

                spyOn($modal, 'open').and.callThrough();

                $scope.editItem(0, 2, iix);

                callArgs = $modal.open.calls.mostRecent().args;
                expect(callArgs.length).toBe(1);
                expect(callArgs[0].templateUrl).toBe('/templates/modals/diagnosis.html/tropical/all');
                expect(callArgs[0].controller).toBe('EditItemCtrl');
                expect(callArgs[0].resolve.item().id).toBeUndefined();
            });
        });
});
