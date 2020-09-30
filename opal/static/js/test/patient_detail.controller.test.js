describe('PatientDetailCtrl', function(){
  "use strict";

  var $scope, $rootScope, $controller, $modal, $routeParams, $httpBackend;
  var patientLoader, Episode, opalTestHelper;
  var patient, controller, metadata, profile;
  var mkcontroller;

  beforeEach(function(){
    module('opal');
    module('opal.test');
    patientLoader = jasmine.createSpy();

    inject(function($injector){
      $rootScope   = $injector.get('$rootScope');
      $scope       = $rootScope.$new();
      $controller  = $injector.get('$controller');
      $modal       = $injector.get('$modal');
      $routeParams = $injector.get('$routeParams');
      $httpBackend = $injector.get('$httpBackend');
      Episode      = $injector.get('Episode');
      opalTestHelper = $injector.get('opalTestHelper');
    });

    // $rootScope.fields = fields;
    // patient = {episodes: [new Episode(angular.copy(episodeData))] };
    patient = opalTestHelper.newPatient($rootScope);
    metadata = opalTestHelper.getMetaData();
    profile = opalTestHelper.getUserProfile();

    mkcontroller = function(patient){
      controller = $controller('PatientDetailCtrl', {
        $scope       : $scope,
        $routeParams : $routeParams,
        patient      : patient,
        profile      : profile,
        metadata     : metadata,
        patientLoader: patientLoader
      });
    };
    mkcontroller(patient);

  });

  describe('initialization', function(){

    it('should set up state', function(){
      expect($scope.patient).toEqual(patient)
    });

    it('should set up the metadata', function(){
      expect($scope.metadata).toEqual(metadata);
    });

    it('should call switch_to_view', function() {
      spyOn($scope, 'switch_to_view');
      $routeParams.view = 'myview';
      $scope.initialise();
      expect($scope.switch_to_view).toHaveBeenCalledWith('myview');
    });

    it('should set the episode', function() {
      spyOn($scope, 'switch_to_episode');
      $routeParams.view = '123';
      $scope.initialise();
      expect($scope.switch_to_episode).toHaveBeenCalledWith(0);
    });

    it('should hoist the metaddata', function(){
      expect($scope.metadata).toBe(metadata);
    });

    describe('with no patient', function() {

      it('should not run initialize.', function() {
        mkcontroller(null);
        expect($scope.epsisode).toBe(undefined);
      });

    });

  });

  describe('switch_to_episode()', function() {

    it('should switch to the episode', function() {
      var mock_event = {preventDefault: jasmine.createSpy()};
      $scope.switch_to_episode(0, mock_event);
      expect($scope.view).toBe(null);
      expect($scope.episode).toBe(patient.episodes[0]);
    });

  });

  describe('refresh()', function(){
    beforeEach(function(){
      var nameChanged = opalTestHelper.getEpisodeData();
      nameChanged.demographics[0].first_name = "Gerald";
      patient = {
        episodes: [new Episode(nameChanged)],
        demographics: [nameChanged.demographics[0]]
      };

      patientLoader.and.returnValue({
        then: function(fn){
          fn(patient);
        }
      });
    });

    it('should refresh the patient', function(){
      $scope.refresh();
      expect($scope.patient.demographics[0].first_name).toBe("Gerald");
    });

    it('should update the current episode on the scope', function(){
      $scope.refresh();
      expect($scope.episode.demographics[0].first_name).toBe("Gerald");
    });

    it('should return a promise that resolve', function(){
      var resolved = false;
      $scope.refresh().then(function(){resolved = true;});
      expect($scope.episode.demographics[0].first_name).toBe("Gerald");
      $scope.$apply();
      expect(resolved).toBe(true);
    });
  });

  describe('switch_to_view()', function() {

    it('should switch', function() {
      $scope.switch_to_view('wat');
      expect($scope.view).toEqual('wat');
    });

  });

});
