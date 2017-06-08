describe('HospitalNumberCtrl', function(){
    "use strict";
    var $scope, $timeout, $modal, modalInstance, $http, $q, $rootScope, $controller;
    var tags, columns, _patientData, patientData, Episode, controller, mkcontroller;
    var $httpBackend, $window;

    var fields = {};
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


    _.each(columns.default, function(c){
        fields[c.name] = c;
    });


    _patientData = {
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
                "category_name": "Inpatient",
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
                "tagging": [{}],
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
        module('opal');
        module('opal.services', function($provide) {
            $provide.value('UserProfile', {
              load: function(){ return profile; }
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
            $window      = $injector.get('$window');
            Episode      = $injector.get('Episode');
        });

        patientData = angular.copy(_patientData);
        modalInstance = $modal.open({template: 'notatemplate'});

        $rootScope.fields = fields;

        mkcontroller = function(with_hosp_num){
            controller = $controller('HospitalNumberCtrl', {
                $scope:         $scope,
                $timeout:       $timeout,
                $modal:         $modal,
                $modalInstance: modalInstance,
                $window:        $window,
                tags:           {tag: 'mine', subtag: ''},
                hospital_number: with_hosp_num
            });
        };
        mkcontroller();

    });

    describe('newly created controller', function(){

        it('should have set up the model', function(){
            expect($scope.model).toEqual({});
        });

        describe('with hospital number', function(){
            it('should store the hospital number', function(){
                mkcontroller('123456789');
                expect($scope.model.hospitalNumber).toEqual('123456789');
            });
        });

    });

    describe('newPatient()', function(){

        it('should open AddEpisodeCtrl', function(){
            var deferred, callArgs;

            deferred = $q.defer();

            spyOn($modal, 'open').and.returnValue({result: deferred.promise});
            $scope.newPatient({patients: [], hospitalNumber: 123})

            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0].controller).toBe('AddEpisodeCtrl');
        });

        it('should provide AddEpisodeCtrl with resolves', function(){
            var deferred, callArgs;

            deferred = $q.defer();

            var fakeReferencedata = {
                load: function(){ return "some reference data"; }
              };


            spyOn($modal, 'open').and.returnValue({result: deferred.promise});
            $scope.newPatient({patients: [], hospitalNumber: 123})
            var resolves = $modal.open.calls.mostRecent().args[0].resolve;
            expect(resolves.referencedata(fakeReferencedata)).toEqual('some reference data');
            expect(resolves.demographics()).toEqual({ hospital_number: 123});
            expect(resolves.tags()).toEqual({tag: 'mine', subtag: ''});
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

    describe('newForPatient()', function(){

        it('should call through if there is an active discharged episode.', function(){
            var deferred, callArgs;
            spyOn($scope, 'newForPatientWithActiveEpisode');

            patientData.active_episode_id = 3;

            deferred = $q.defer();
            spyOn($modal, 'open').and.returnValue({result: deferred.promise});

            $scope.newForPatient(patientData);

            callArgs = $modal.open.calls.mostRecent().args;
            expect(callArgs.length).toBe(1);
            expect(callArgs[0].controller).toBe('AddEpisodeCtrl');
            var resolves = $modal.open.calls.mostRecent().args[0].resolve;
            expect(_.has(resolves, 'referencedata')).toBe(true);
            var expected_demographics = angular.copy(patientData.demographics[0])
            expected_demographics["date_of_birth"] = "12/12/1999";
            expect(resolves.demographics()).toEqual(expected_demographics);
            expect(resolves.tags()).toEqual({tag: 'mine', subtag: ''});
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

    describe('addForPatientWithActiveEpisode()', function(){
        var activePatientData;

        beforeEach(function(){
            activePatientData = angular.copy(patientData);
            activePatientData.active_episode_id = 3;
        })

        describe('if not an inpatient', function(){
            it('should add an episode', function(){
                spyOn($scope, 'addForPatient');
                activePatientData.episodes[3].category_name = 'outpatients';
                $scope.newForPatientWithActiveEpisode(activePatientData);
                expect($scope.addForPatient).toHaveBeenCalledWith(activePatientData);
            })
        });

        describe('if we have the current tags', function(){
            it('should just close', function(){
                spyOn(modalInstance, 'close');
                activePatientData.episodes[3].tagging[0].mine = true;
                $scope.newForPatientWithActiveEpisode(activePatientData);
                expect(modalInstance.close).toHaveBeenCalled();
            })
        });

        describe('if we have the current tag but not hte subtag', function(){
            it('should add the tag', function(){
                spyOn(modalInstance, 'close');
                $scope.tags.tag = 'main';
                $scope.tags.subtag = 'secondary';

                activePatientData.episodes[3].tagging[0].main = true;

                $httpBackend.expectPUT('/api/v0.1/tagging/3/',
                                       {main: true, secondary: true, id: 3})
                    .respond({});

                $scope.newForPatientWithActiveEpisode(activePatientData);
                $scope.$digest();
                $httpBackend.flush()
                expect(modalInstance.close).toHaveBeenCalled();

            });
        });

    });

    describe('findByHospitalNumber()', function(){
      it("should handle error's", function(){
        spyOn(Episode, 'findByHospitalNumber');
        spyOn($window, 'alert');
        spyOn(modalInstance, 'close');
        $scope.modal = {hospitalNumber: "1"};
        $scope.findByHospitalNumber();
        expect(Episode.findByHospitalNumber).toHaveBeenCalled();
        var callArgs = Episode.findByHospitalNumber.calls.argsFor(0);
        callArgs[1].error();

        expect($window.alert).toHaveBeenCalledWith('ERROR: More than one patient found with hospital number');
        expect(modalInstance.close).toHaveBeenCalledWith(null);
      });
    });

    describe('addForPatient()', function(){

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
            episode = new Episode({
                id: 3,
                demographics: [{"patient_id": 1}]
            });

            spyOn($modal, 'open').and.returnValue({result: deferred.promise});
            spyOn(modalInstance, 'close');

            $scope.addForPatient(patientData);

            deferred.resolve(episode);
            $rootScope.$apply();

            callArgs = modalInstance.close.calls.mostRecent().args;
            expect(callArgs[0].makeCopy()).toEqual(episode.makeCopy());
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
