var app = OPAL.module('opalTest', []);

angular.module('opalTest').service('testHelper', function(Episode){
  "use strict";

  var episodeData = {
    id: 123,
    active: true,
    category_name: "Inpatient",
    prev_episodes: [],
    next_episodes: [],
    demographics: [{
      id: 101,
      patient_id: 99,
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
    diagnosis: [
      {
        id: 102,
        condition: 'Dengue',
        provisional: true,
      },
      {
        id: 103,
        condition: 'Malaria',
        provisional: false,
      }
    ]
  };

  var recordLoaderData = {
    demographics: {
      name: 'demographics',
      single: true,
      fields: [
          {name: 'name', type: 'string'},
          {name: 'date_of_birth', type: 'date'},
          {name: 'date_of_admission', type: 'date'},
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
      fields: [
          {name: 'condition', type: 'string'},
          {name: 'provisional', type: 'boolean'},
      ]
    },
    investigation: {
      name:  'investigation',
      single: false,
      fields: [
          {name: 'result', type: 'string'},
      ]
    },
    microbiology_test: {
      name:  'microbiology_test',
      single: false,
      fields: [
          {name: 'result', type: 'string'},
          {name: 'consistency_token', type: 'string'},
          {name: 'test', type: 'string'},
          {name: 'c_difficile_toxin', type: 'string'}
      ]
    }
  };

  var metadata = {
      tag_hierarchy :{'tropical': []},
      micro_test_defaults: {
          micro_test_c_difficile: {
              c_difficile_antigen: "pending",
              c_difficile_toxin: "pending"
          }
      },
      macros: []
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

    spyOn(loader.load).and.callThrough();
    return loader;
  };

  var userProfile = {
      readonly   : false,
      can_extract: true,
      can_see_pid: function(){return true; }
  };

  return {
    newEpisode: function(rootScope){
      rootScope.fields = angular.copy(recordLoaderData);
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
