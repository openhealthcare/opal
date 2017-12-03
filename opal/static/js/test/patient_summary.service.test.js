describe('PatientSummary', function (){
  "use strict";
  var PatientSummary;
  var testData;

  beforeEach(function(){
    module('opal.services');
    inject(function($injector){
        PatientSummary = $injector.get('PatientSummary');
    });

    testData = {
      categories: ["Inpatient", "WalkIn"],
      count: 1,
      date_of_birth: "12/05/1973",
      first_name: "Isabella",
      hospital_number: "11111111",
      id: 192,
      patient_id: 192,
      surname: "King"
    };
  });

  it("should populate a patient summary", function(){
      var patientSummary = new PatientSummary(testData);
      expect(patientSummary.categories).toEqual("Inpatient, WalkIn");
      expect(patientSummary.dateOfBirth.toDate()).toEqual(new Date(1973, 4, 12));
      expect(patientSummary.years).toEqual(undefined);
      expect(patientSummary.hospitalNumber).toEqual("11111111");
      expect(patientSummary.first_name).toEqual("Isabella");
      expect(patientSummary.surname).toEqual("King");
      expect(patientSummary.link).toEqual("/#/patient/192");
      expect(patientSummary.patientId).toEqual(192);
  });

  it("should populate years if they exist", function(){
      testData.start_date = "10/10/1973";
      testData.end_date = "10/10/1974";
      var patientSummary = new PatientSummary(testData);
      expect(patientSummary.years).toEqual("1973-1974");
  });

  it("should only use start date if there's only start date", function(){
      testData.start_date = "10/10/1973";
      var patientSummary = new PatientSummary(testData);
      expect(patientSummary.years).toEqual("1973");
  });

  it("should use undefined if there's only end date", function(){
      testData.end_date = "10/10/1973";
      var patientSummary = new PatientSummary(testData);
      expect(patientSummary.years).toEqual(undefined);
  });

  it("if the start date year equals the end date year, we only need the year", function(){
      testData.start_date = "9/10/1973";
      testData.end_date = "10/10/1973";
      var patientSummary = new PatientSummary(testData);
      expect(patientSummary.years).toEqual("1973");
  });
});
