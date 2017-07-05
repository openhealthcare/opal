describe('FindPatientCtrl', function() {
  "use strict";
  var scope, Episode, $controller, controller, $alert;

  beforeEach(function(){
    module('opal.controllers');
    inject(function($injector){
      var $rootScope = $injector.get('$rootScope');
      scope = $rootScope.$new();
      Episode = $injector.get('Episode');
      $controller = $injector.get('$controller');
    });

    $alert = jasmine.createSpy();

    scope.pathway = {
      save_url: "/some_url"
    };
    controller = $controller('FindPatientCtrl', {
      scope: scope,
      Episode: Episode,
      step: {},
      episode: {},
      $alert: $alert
    });
  });

  it("should initialise the scope", function(){
    var fakeScope = {};
    controller.initialise(fakeScope);
    expect(fakeScope.demographics.hospital_number).toBe(undefined);
    expect(fakeScope.state).toBe('initial');
  });

  it("should change scope if we're unable to find a patient", function(){
    expect(scope.state).toBe('initial');
    scope.new_patient();
    expect(scope.state).toBe('editing_demographics');
  });

  it("should look up hospital numbers", function(){
    spyOn(Episode, "findByHospitalNumber");
    scope.demographics.hospital_number = "12";
    scope.lookup_hospital_number();
    var allCallArgs = Episode.findByHospitalNumber.calls.all();
    expect(allCallArgs.length).toBe(1);
    var callArgs = allCallArgs[0].args;
    expect(callArgs[0]).toBe("12");
    expect(callArgs[1].newPatient).toEqual(scope.new_patient);
    expect(callArgs[1].newForPatient).toEqual(scope.new_for_patient);
  });

  it("should throw an error if the hospital number isn't found", function(){
    spyOn(Episode, "findByHospitalNumber");
    scope.demographics.hospital_number = "12";
    scope.lookup_hospital_number();
    var allCallArgs = Episode.findByHospitalNumber.calls.all();
    expect(allCallArgs.length).toBe(1);
    var callArgs = allCallArgs[0].args;
    expect(callArgs[1].error());
    expect($alert).toHaveBeenCalledWith('ERROR: More than one patient found with hospital number');
  });

  it('should only show next if state is has_demographics or editing_demographics', function(){
    scope.state = "has_demographics";
    expect(scope.showNext()).toBe(true);
    scope.state = "editing_demographics";
    expect(scope.showNext()).toBe(true);
  });

  it('should only show next if state is neither has_demographics or editing_demographics', function(){
    scope.state = "something";
    expect(scope.showNext()).toBe(false);
  });

  it('should update the next save_url if an patient is found', function(){
    scope.demographics = {patient_id: 1};
    scope.preSave({});
    expect(scope.pathway.save_url).toBe("/some_url/1");
  });

  it('should not update the next save_url if an patient is not found', function(){
    scope.preSave({});
    expect(scope.pathway.save_url).toBe("/some_url");
  });

  it("should update the demographics if a patient is found", function(){
    var fakePatient = {demographics: [{hospital_number: "1"}]};
    scope.new_for_patient(fakePatient);
    expect(scope.state).toBe('has_demographics');
    expect(scope.demographics).toBe(fakePatient.demographics[0]);
  });

  it("should hoist demographics to editing before saving", function(){
    scope.demographics = {hospital_number: "1"};
    var editing = {};
    scope.preSave(editing);
    expect(editing.demographics).toEqual(scope.demographics);
  });
});
