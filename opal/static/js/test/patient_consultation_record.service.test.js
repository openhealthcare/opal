describe('PatientConsultation', function() {
  "use strict";
  var $window, PatientConsultationRecord;

  beforeEach(function(){
    module('opal.services', function($provide){
      $provide.service('$window', function(){
        return {initials: "J Fonda"};
      });
    });
    inject(function($injector){
      PatientConsultationRecord = $injector.get('PatientConsultationRecord');
    });

  });

  it('should add initials off the window and when if not set', function(){
    var today = moment().format("DD/MM/YYYY");
    var patient_consultation_record = {};
    PatientConsultationRecord(patient_consultation_record);
    expect(patient_consultation_record.when.format("DD/MM/YYYY")).toEqual(today);
    expect(patient_consultation_record.initials).toEqual("J Fonda");
  });

  it('should not trash existing initials', function() {
    var patient_consultation_record = {initials: 'JFK'};
    PatientConsultationRecord(patient_consultation_record);
    expect(patient_consultation_record.initials).toEqual("JFK");
  });

});
