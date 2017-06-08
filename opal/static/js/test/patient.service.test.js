//
// Unit tests for our patient loader service
//
describe('Patient', function() {
  "use strict";

  var $httpBackend, $route, $rootScope, Patient, EpisodeSpy;

  var patientData = {
    id: 1,
    demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}],
    episodes: {
      122: {id: 122, start: "20/01/2016", end: "20/02/2016", demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]},
      123: {id: 123, start: "20/01/2016", end: undefined, demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]},
      124: {id: 124, start: undefined, end: "20/03/2016", demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]},
      125: {id: 125, start: undefined, end: undefined, demographics: [{first_name: "Sue", surname: "Jackson", patient_id: 1}]}
    }
  };

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
    ]
  };
  _.each(records.default, function(c){
    fields[c.name] = c;
  });

  beforeEach(function(){
    module('opal.services');

    inject(function($injector){
      Patient = $injector.get('Patient');
      $httpBackend  = $injector.get('$httpBackend');
      $route        = $injector.get('$route');
      $rootScope    = $injector.get('$rootScope');
    });

    $route.current = { params: { patient_id: '123' } };
    $rootScope.fields = angular.copy(fields);
  });

  describe('patient', function() {
    it('should sort patient episodes', function() {
      // patients are sorted negatively by end date, if it
      // exists and start date if it doesn't
      var patient = new Patient(patientData);
      expect(patient.episodes[0].id).toBe(124);
      expect(patient.episodes[1].id).toBe(122);
      expect(patient.episodes[2].id).toBe(123);
      expect(patient.episodes[3].id).toBe(125);
    });

    it('should cast the patient subrecords to items', function(){
      var patient = new Patient(patientData);
      expect(patient.demographics[0].first_name).toBe('Sue');
    });

    it('should hoise the first episodes record editor onto it', function(){
      var patient = new Patient(patientData);

      // they should both be pointing at the same object
      expect(patient.recordEditor).toBe(patient.episodes[0].recordEditor);

      // they should not be null
      expect(!!patient.recordEditor).toBe(true);
    });

    it('should not hoist the id field', function(){
      var patient = new Patient(patientData);
      expect(patient.id).toBe(1);
    });
  });
});
