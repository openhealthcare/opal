(function(){
  var app = OPAL.module('opal.test', []);

  angular.module('opal.test').service('opalTestHelper', function(Patient, Episode){
    "use strict";

    var demographics = [{
      id: 101,
      patient_id: 99,
      first_name: "John",
      surname: "Smith",
      hospital_number: '1111111111',
      date_of_birth: '31/07/1980',
      created: "07/04/2015 11:45:00"
    }]

    var episodeData = {
      id: 123,
      active: true,
      category_name: "Inpatient",
      consistency_token: undefined,
      prev_episodes: [],
      start: "19/11/2013",
      end: "25/05/2016",
      demographics: demographics,
      tagging: [{'mine': true, 'tropical': true}],
      location: [{
        category: 'Inpatient',
        hospital: 'UCH',
        ward: 'T10',
        bed: '15',
        date_of_admission: '01/08/2013',
      }],
      diagnosis: [
        {
          id: 102,
          condition: 'Dengue',
          provisional: true,
          date_of_diagnosis: '01/06/2013'
        },
        {
          id: 103,
          condition: 'Malaria',
          provisional: false,
          date_of_diagnosis: '01/07/2013'
        }
      ]
    };

    var patientData = {
      id: 1,
      demographics: demographics,
      episodes: {
        "123": episodeData
      }
    }

    var recordLoaderData = {
      demographics: {
        name: 'demographics',
        single: true,
        fields: [
            {name: 'first_name', type: 'string'},
            {name: 'surname', type: 'string'},
            {name: 'date_of_birth', type: 'date'},
            {name: 'date_of_admission', type: 'date'},
            {name: 'created', type: 'date_time'}
        ]
      },
      location: {
        name: 'location',
        single: true,
        fields: [
            {name: 'category', type: 'string'},
            {name: 'hospital', type: 'string'},
            {name: 'ward', type: 'string'},
            {name: 'bed', type: 'string'},
            {name: 'date_of_admission', type: 'date'},
            {name: 'tags', type: 'list'},
        ]
      },
      diagnosis: {
        name: 'diagnosis',
        single: false,
        icon: "fa fa-stethoscope",
        sort: "date_of_diagnosis",
        fields: [
            {name: 'condition', type: 'string'},
            {name: 'provisional', type: 'boolean'},
            {name: 'date_of_diagnosis', type: 'date'},
        ]
      },
      tagging: {
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
    };

    var metadata = {
        tag_hierarchy :{'tropical': [], 'inpatients': ['icu']},
        micro_test_defaults: {
            micro_test_c_difficile: {
                c_difficile_antigen: "pending",
                c_difficile_toxin: "pending"
            }
        },
        tag_display: {'tropical': 'Tropical', 'icu': "ICU"},
        tags: {
            opat_referrals: {
                display_name: "OPAT Referral",
                parent_tag: "opat",
                name: "opat_referrals"
            },
            tropical: {
                display_name: "Tropical",
                name: "tropical"
            },
            mine: {
                direct_add: true,
                display_name: 'Mine',
                name: 'mine',
                slug: 'mine'
            },
            icu: {
                direct_add: true,
                display_name: 'ICU',
                name: 'icu',
                slug: 'icu'
            }
        }
    };

    var referencedata = {
        micro_test_c_difficile: [
            "C diff", "Clostridium difficile"
        ],
        micro_test_stool_parasitology_pcr: [
            "Stool Parasitology PCR"
        ],
        micro_test_defaults: {
            micro_test_c_difficile: {
                c_difficile_antigen: "pending",
                c_difficile_toxin: "pending"
            }
        },
        toLookuplists: function(){return {}; }
    };

    var getLoaderMock = function(returnValue){
      var loader = {
        load: function(){
          return {
            then: function(fn){
              fn(angular.copy(returnValue));
            }
          };
        }
      };

      spyOn(loader, "load").and.callThrough();
      return loader;
    };

    var userProfile = {
        readonly   : false,
        can_extract: true,
    };

    return {
      newPatient: function(rootScope){
        rootScope.fields = angular.copy(recordLoaderData);
        return new Patient(angular.copy(patientData));
      },
      getPatientData: function(){
        return angular.copy(patientData);
      },
      newEpisode: function(rootScope, ed){
        rootScope.fields = angular.copy(recordLoaderData);
        if(ed){
          return new Episode(ed);
        }

        return new Episode(episodeData);
      },
      getEpisodeData: function(){
        return angular.copy(episodeData);
      },
      getRecordLoader: function(){
        return getLoaderMock(recordLoaderData);
      },
      getRecordLoaderData: function(){
        return angular.copy(recordLoaderData);
      },
      getMetaDataLoader: function(){
        return getLoaderMock(metadata);
      },
      getMetaData: function(){
        return angular.copy(metadata);
      },
      getReferenceDataLoader: function(){
        return getLoaderMock(referencedata);
      },
      getReferenceData: function(){
        return angular.copy(referencedata);
      },
      getUserProfileLoader: function(){
        return getLoaderMock(userProfile);
      },
      getUserProfile: function(){
        return angular.copy(userProfile);
      }
    };
  });
})();
