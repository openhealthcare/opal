describe('ReopenEpisodeCtrl', function (){
    "use strict"
    var $scope,  $timeout, $rootScope, $httpBackend;
    var Episode;
    var dialog, patient, tag, subtag;
    var modalInstance, mkcontroller;
    var fields = {};
    var subrecords = {
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
                    }
                ]
            }
        ]
    };


    _.each(subrecords.default, function(c){
        fields[c.name] = c;
    });

    var patientData = {
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
                "tagging": [{

                }],
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
            $rootScope   = $injector.get('$rootScope');
            $scope       = $rootScope.$new();
            $controller  = $injector.get('$controller');
            $modal       = $injector.get('$modal');
            $timeout     = $injector.get('$timeout');
            Episode      = $injector.get('Episode');
            $httpBackend = $injector.get('$httpBackend');
        });

        $rootScope.fields = fields;
        modalInstance = $modal.open({template: 'notarealtemplate!'});
        patient = angular.copy(patientData);
        patient.episodes = _.map(_.keys(patient.episodes), function(k){
            return new Episode(patientData.episodes[k]);
        })
        tag = 'mine';
        subtag = null;


        mkcontroller = function(){
            $controller('ReopenEpisodeCtrl', {
                $scope  : $scope,
                $timeout: $timeout,
                $modalInstance  : modalInstance,
                patient : patient,
                tag     : tag,
                subtag  : subtag,
            });
        }
        mkcontroller();
    });

    describe('initialization', function(){
        it('should set up state', function(){
            expect($scope.episodes.length).toEqual(1);
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

    describe('reopen()', function() {
      it('should save with the tags.', function() {
          $httpBackend.expectGET('/api/v0.1/userprofile/').respond({});
          tag = 'id';
          subtag = 'inpatients';
          mkcontroller();
          $scope.model.episodeId = '0';
          $scope.reopen();
          $httpBackend.flush();
          $rootScope.$apply();
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
