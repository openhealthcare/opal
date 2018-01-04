describe('PathwayCtrl', function() {
  "use strict";
  var $scope,  $controller, controller, metadata;
  var referencedata, pathwayDefinition;
  var $window;

  beforeEach(function(){
    module('opal.controllers');
    referencedata = jasmine.createSpyObj(["toLookuplists"]);
    referencedata.toLookuplists.and.returnValue({some: "data"});

    var _$injector;
    inject(function($injector){
      var $rootScope = $injector.get('$rootScope');
      $scope = $rootScope.$new();
      $controller = $injector.get('$controller');
      $window = $injector.get('$window');
    });

    pathwayDefinition = {
      pathway_service: "Pathway"
    };

    metadata = {"fake": "metadata"};
    $window = jasmine.createSpyObj(["alert"]);
    $window.location = {href: ""};

    $controller('PathwayCtrl', {
      $scope: $scope,
      episode: null,
      referencedata: referencedata,
      metadata: metadata,
      pathwayDefinition: pathwayDefinition,
      $window: $window
    });
  });

  it('should put metadata on to the scope', function(){
    expect($scope.metadata).toEqual(metadata);
  });

  it('should put referencedata on to the scope', function(){
    expect($scope.some).toBe("data");
    expect(referencedata.toLookuplists).toHaveBeenCalled();
  });

  it('should close the instance if the call back returns a string', function(){
    $scope.pathway.pathwayResult.resolve({redirect_url: "somewhere"});
    $scope.$apply();
    expect($window.location.href).toEqual("somewhere");
  });

  it('should close the instance if the call back is rejected', function(){
    $scope.pathway.pathwayResult.reject("done");
    $scope.$apply();
    expect($window.alert).toHaveBeenCalledWith("unable to save patient");
  });
});
