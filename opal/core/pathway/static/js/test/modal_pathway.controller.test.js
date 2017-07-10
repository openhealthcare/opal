describe('ModalPathwayCtrl', function() {
  "use strict";
  var $scope,  $controller, controller, metadata, testHelper;
  var referencedata, pathwayDefinition, pathwayCallback;
  var $modalInstance, $window, $analytics, mkController, $rootScope;

  beforeEach(function(){
    module('opal.controllers');

    referencedata = jasmine.createSpyObj(["toLookuplists"]);
    referencedata.toLookuplists.and.returnValue({some: "data"});
    $modalInstance = jasmine.createSpyObj(["close"]);
    $analytics = jasmine.createSpyObj(["eventTrack"]);

    inject(function($injector){
      $rootScope = $injector.get('$rootScope');
      $controller = $injector.get('$controller');
      $window = $injector.get('$window');
    });

    $scope = $rootScope.$new();
    pathwayDefinition = {
      pathway_service: "Pathway"
    };

    metadata = {"fake": "metadata"};
    pathwayCallback = jasmine.createSpy();

    mkController = function(){
      $controller('ModalPathwayCtrl', {
          $scope: $scope,
          episode: null,
          referencedata: referencedata,
          metadata: metadata,
          pathwayDefinition: pathwayDefinition,
          $modalInstance: $modalInstance,
          pathwayCallback: pathwayCallback,
          pathwayName: "somePathway",
          $window: $window,
          $analytics: $analytics
      });
    };
  });

  it('should put metadata on to the scope', function(){
    mkController();
    expect($scope.metadata).toEqual(metadata);
  });

  it('should log analytics on pathway use', function(){
    mkController();
    expect($analytics.eventTrack).toHaveBeenCalledWith(
      'somePathway', {category: "ModalPathway"}
    );
  });

  it('should log analytics with episode category if provided', function(){
    $controller('ModalPathwayCtrl', {
        $scope: $scope,
        episode: {category_name: "some category"},
        referencedata: referencedata,
        metadata: metadata,
        pathwayDefinition: pathwayDefinition,
        $modalInstance: $modalInstance,
        pathwayCallback: pathwayCallback,
        pathwayName: "somePathway",
        $window: $window,
        $analytics: $analytics
    });
    expect($analytics.eventTrack).toHaveBeenCalledWith(
      'somePathway', {category: "ModalPathway", label: "some category"}
    );
  });

  it('should put referencedata on to the scope', function(){
    mkController();
    expect($scope.some).toBe("data");
    expect(referencedata.toLookuplists).toHaveBeenCalled();
  });

  it('should close the instance if the call back returns a promise', function(){
    mkController();
    pathwayCallback.and.returnValue({
      then: function(fn){ fn("something"); }
    });
    $scope.pathway.pathwayResult.resolve("done");
    $scope.$apply();
    expect(pathwayCallback).toHaveBeenCalledWith("done");
    expect($modalInstance.close).toHaveBeenCalledWith("something");
  });

  it('should close the instance if the call back returns a string', function(){
    mkController();
    pathwayCallback.and.returnValue("something");
    $scope.pathway.pathwayResult.resolve("done");
    $scope.$apply();
    expect(pathwayCallback).toHaveBeenCalledWith("done");
    expect($modalInstance.close).toHaveBeenCalledWith("something");
  });

  it('should close the instance if the call back returns a string', function(){
    mkController();
    $scope.pathway.pathwayResult.resolve();
    $scope.$apply();
    expect($modalInstance.close).toHaveBeenCalledWith();
  });

  it('should close the instance if the call back is rejected', function(){
    mkController();
    spyOn($window, "alert");
    pathwayCallback.and.returnValue("something");
    $scope.pathway.pathwayResult.reject("done");
    $scope.$apply();
    expect($window.alert).toHaveBeenCalledWith("unable to save patient");
  });

});
