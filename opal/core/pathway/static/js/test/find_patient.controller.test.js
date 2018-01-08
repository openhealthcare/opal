describe('FindPatientCtrl', function() {
  "use strict";
  var scope, Episode, $controller, controller, $window;
  var opalTestHelper, $rootScope, Pathway;

  var pathwayDefinition = {
    icon: undefined,
    save_url: '/some_url',
    pathway_service: 'Pathway',
    finish_button_icon: "fa fa-save",
    finish_button_text: "Save",
    steps: [
      {
        'step_controller': 'FindPatientCtrl',
        'icon': 'fa fa-user',
        'template_url': '/templates/pathway/find_patient_form.html',
        'title': 'Find Patient'
      },
      {
        'api_name': 'location',
        'step_controller': 'DefaultStep',
        'icon': 'fa fa-map-marker',
        'template_url': '/templates/pathway/blood_culture_location.html',
        'title': 'Location'
      }
    ],
    display_name: 'Add Patient'
  };

  beforeEach(function(){
    module('opal.controllers');
    module('opal.test');
    inject(function($injector){
      $rootScope = $injector.get('$rootScope');
      scope = $rootScope.$new();
      Episode = $injector.get('Episode');
      Pathway = $injector.get('Pathway');
      $controller = $injector.get('$controller');
      opalTestHelper = $injector.get('opalTestHelper');
    });

    $window = {alert: jasmine.createSpy()};
    scope.editing = {};
    scope.pathway = new Pathway(pathwayDefinition);
    $rootScope.fields = opalTestHelper.getRecordLoaderData();

    controller = $controller('FindPatientCtrl', {
      scope: scope,
      Episode: Episode,
      step: {},
      episode: {},
      $window: $window
    });
  });

  it("should initialise the scope", function(){
    controller.initialise(scope);
    expect(scope.editing.demographics.length).toBe(1);
    expect(scope.state).toBe('initial');
  });

  it("should change scope if we're unable to find a patient", function(){
    controller.initialise(scope);
    expect(scope.state).toBe('initial');
    scope.new_patient();
    expect(scope.state).toBe('editing_demographics');

    // hoist an empty array on to the scope
    expect(scope.editing.demographics.length).toEqual(1);
  });

  it("should look up hospital numbers", function(){
    spyOn(Episode, "findByHospitalNumber");
    controller.initialise(scope);
    scope.editing.demographics[0].hospital_number = "12";
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
    scope.editing = {};
    controller.initialise(scope);
    scope.lookup_hospital_number();
    var allCallArgs = Episode.findByHospitalNumber.calls.all();
    expect(allCallArgs.length).toBe(1);
    var callArgs = allCallArgs[0].args;
    expect(callArgs[1].error());
    expect($window.alert).toHaveBeenCalledWith('ERROR: More than one patient found with hospital number');
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
    scope.preSave({demographics: {patient_id: 1}});
    expect(scope.pathway.save_url).toBe("/some_url/1");
  });

  it('should not update the next save_url if an patient is not found', function(){
    scope.preSave({});
    expect(scope.pathway.save_url).toBe("/some_url");
  });

  it("should update the demographics if a patient is found", function(){
    var newPatient = opalTestHelper.getPatientData();
    newPatient.demographics[0].first_name = "Larry";
    scope.new_for_patient(newPatient);
    expect(scope.state).toBe('has_demographics');
    expect(scope.editing.demographics[0].first_name).toBe("Larry");
  });
});
