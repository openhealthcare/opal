//
// Unit tests for our patient loader service
//
describe('Patient', function() {
  "use strict";

  var $httpBackend, $route, $rootScope, Patient, patientData;
  var opalTestHelper, episodeData;

  beforeEach(function(){
    module('opal.services');
    module('opal.test');

    inject(function($injector){
      Patient = $injector.get('Patient');
      $httpBackend  = $injector.get('$httpBackend');
      $route        = $injector.get('$route');
      $rootScope    = $injector.get('$rootScope');
      opalTestHelper    = $injector.get('opalTestHelper');
    });

    patientData = opalTestHelper.getPatientData();
    episodeData = opalTestHelper.getEpisodeData();

    var episodeData122 = _.extend(angular.copy(episodeData), {
      id: 122, start: "20/01/2016", end: "20/02/2016"
    });
    var episodeData123 = _.extend(angular.copy(episodeData), {
      id: 123, start: "20/01/2016", end: undefined
    });
    var episodeData124 = _.extend(angular.copy(episodeData), {
      id: 124, start: undefined, end: "20/03/2016"
    });

    var episodeData125 = _.extend(angular.copy(episodeData), {
      id: 125, start: undefined, end: undefined
    });

    patientData.episodes = {};
    _.each([episodeData122, episodeData123, episodeData124, episodeData125], function(e){
      patientData.episodes[e.id] = e;
    });

    $rootScope.fields = opalTestHelper.getReferenceData();
    $route.current = { params: { patient_id: '123' } };
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
      expect(patient.demographics[0].first_name).toBe('John');
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
