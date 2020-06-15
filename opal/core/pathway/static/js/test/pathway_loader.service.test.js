describe('pathwayLoader', function() {
  "use strict";
  var pathwayLoader, $window, $httpBackend;
  var episode = {
    id: 10,
    demographics: [{
      patient_id: 12
    }]
  };

  beforeEach(function(){
    module('opal.services');
    inject(function($injector) {
      pathwayLoader = $injector.get('pathwayLoader');
      $window = $injector.get('$window');
      $httpBackend = $injector.get('$httpBackend');
    });
  });

  it('should get the pathway from a url and return a promise', function(){
    $httpBackend.expectGET("/pathway/detail/somePathway").respond({});
    var result = pathwayLoader.load("somePathway", null);
    $httpBackend.flush();
    $httpBackend.verifyNoOutstandingRequest();
    $httpBackend.verifyNoOutstandingExpectation();
    expect(!!result.then).toBe(true);
  });

  it('should add the patient id if the episode id is not provided', function(){
    $httpBackend.expectGET("/pathway/detail/somePathway/12").respond({});
    pathwayLoader.load("somePathway", 12);
    $httpBackend.flush();
    $httpBackend.verifyNoOutstandingRequest();
    $httpBackend.verifyNoOutstandingExpectation();
  });

  it('should add the episode id/patient id if provided', function(){
    $httpBackend.expectGET("/pathway/detail/somePathway/12/10").respond({});
    pathwayLoader.load("somePathway", 12, 10);
    $httpBackend.flush();
    $httpBackend.verifyNoOutstandingRequest();
    $httpBackend.verifyNoOutstandingExpectation();
  });

  it('should add an is_modal get param if appropriate', function(){
    $httpBackend.expectGET("/pathway/detail/somePathway/12/10").respond({});
    pathwayLoader.load("somePathway", 12, 10);
    $httpBackend.flush();
    $httpBackend.verifyNoOutstandingRequest();
    $httpBackend.verifyNoOutstandingExpectation();
  });

  it('should raise an error if the pathway fails to load', function(){
    spyOn($window, 'alert');
    $httpBackend.expectGET('/pathway/detail/somePathway').respond(
      409, {'error': 'Pathway not found'}
    );
    pathwayLoader.load("somePathway", null);
    $httpBackend.flush();
    $httpBackend.verifyNoOutstandingRequest();
    $httpBackend.verifyNoOutstandingExpectation();
    expect($window.alert).toHaveBeenCalledWith('Pathway could not be loaded');
  });
});
