describe('HospitalNumberCtrl', function(){
    var $scope, $timeout, $modal, modalInstance, $http, $q;
    var tags, columns, patientData, Episode;

    optionsData = {
        condition: ['Another condition', 'Some condition'],
        tag_hierarchy :{'tropical': []}
    }

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

    beforeEach(function(){
        module('opal', function($provide) {
            $provide.value('$analytics', function(){
                return {
                    pageTrack: function(x){}
                }
            });

            $provide.provider('$analytics', function(){
                this.$get = function() {
                    return {
                        virtualPageviews: function(x){},
                        settings: {
                            pageTracking: false,
                        },
                        pageTrack: function(x){}
                     };
                };
            });
        });
    });

    beforeEach(function(){
        inject(function($injector){
            $httpBackend = $injector.get('$httpBackend');
            $rootScope   = $injector.get('$rootScope');
            $scope       = $rootScope.$new();
            $q           = $injector.get('$q');
            $controller  = $injector.get('$controller');
            $timeout     = $injector.get('$timeout');
            $modal       = $injector.get('$modal');
            Episode = $injector.get('Episode');
        });

        options = optionsData;
        modalInstance = $modal.open({template: 'notatemplate'});
        schema = new Schema(columns.default);

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

            spyOn($modal, 'open').and.returnValue({result: deferred.promise});
            $scope.newPatient({patients: [], hospitalNumber: 123})

            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0].controller).toBe('AddEpisodeCtrl');
        });

        it('should close the modal with a new patient', function(){
            var deferred;

            deferred = $q.defer();

            spyOn($modal, 'open').and.returnValue({result: deferred.promise});
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
            spyOn($modal, 'open').and.returnValue({result: deferred.promise});

            $scope.newForPatient(patientData);

            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0].controller).toBe('AddEpisodeCtrl');
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
            patient = angular.copy(patientData);
            patient.active_episode_id = undefined;
            patient.episodes = {};
            $scope.newForPatient(patient);
            expect($scope.addForPatient).toHaveBeenCalledWith(patient);
        });

        it('should offer to reopen episodes', function(){
            var deferred, callArgs;

            deferred = $q.defer();
            spyOn($modal, 'open').and.returnValue({result: deferred.promise});

            $scope.newForPatient(patientData);

            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0].controller).toBe('AddEpisodeCtrl');
        });

        it('should open a new episode', function(){
            var deferred;

            deferred = $q.defer();
            spyOn($modal, 'open').and.returnValue({result: deferred.promise});
            spyOn($scope, 'addForPatient');

            $scope.newForPatient(patientData);
            deferred.resolve('open-new');

            $rootScope.$apply();

            expect($scope.addForPatient).toHaveBeenCalledWith(patientData);
        });

        it('should pass through the reopened episode', function(){
            var deferred;

            deferred = $q.defer();
            spyOn($modal, 'open').and.returnValue({result: deferred.promise});
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

            spyOn($modal, 'open').and.returnValue({result: deferred.promise});

            $scope.addForPatient(patientData);

            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0].controller).toBe('AddEpisodeCtrl');
        });

        it('should pass through demographics', function(){
            var deferred, callArgs;

            deferred = $q.defer();

            spyOn($modal, 'open').and.returnValue({result: deferred.promise});

            $scope.addForPatient(patientData);

            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0].resolve.demographics())
                .toEqual(patientData.demographics[0]);
        });

        it('should close the dialog with the new episode', function(){
            var deferred, episode, callArgs;

            deferred = $q.defer();
            episode = new Episode({id: 3}, schema);

            spyOn($modal, 'open').and.returnValue({result: deferred.promise});
            spyOn(modalInstance, 'close');

            $scope.addForPatient(patientData);

            deferred.resolve(episode);
            $rootScope.$apply();

            callArgs = modalInstance.close.calls.mostRecent().args;
            expect(callArgs[0].makeCopy()).toEqual(episode.makeCopy());
        });

    });

    describe('cancelling the modal', function(){
        it('should close with null', function(){
            spyOn(modalInstance, 'close');
            $scope.cancel();
            expect(modalInstance.close).toHaveBeenCalledWith(null);
        });
    });

});
