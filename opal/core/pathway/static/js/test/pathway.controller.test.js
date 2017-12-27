describe('PathwayCtrl', function() {
  "use strict";
  var $scope,  $controller, controller, metadata;
  var referencedata, pathwayDefinition, mkController;
  var $window, opalTestHelper, $rootScope;

  beforeEach(function(){
    module('opal.controllers');
    module('opal.test');
    referencedata = jasmine.createSpyObj(["toLookuplists"]);
    referencedata.toLookuplists.and.returnValue({some: "data"});

    var _$injector;
    inject(function($injector){
      $rootScope = $injector.get('$rootScope');
      $scope = $rootScope.$new();
      $controller = $injector.get('$controller');
      $window = $injector.get('$window');
      opalTestHelper = $injector.get('opalTestHelper');
    });

    pathwayDefinition = {
      pathway_service: "Pathway"
    };

    metadata = {"fake": "metadata"};
    $window = jasmine.createSpyObj(["alert"]);
    $window.location = {href: ""};

    mkController = function(episode){
      $controller('PathwayCtrl', {
        $scope: $scope,
        episode: episode,
        referencedata: referencedata,
        metadata: metadata,
        pathwayDefinition: pathwayDefinition,
        $window: $window
      });
    };
  });

  it('should put metadata on to the scope', function(){
    mkController();
    expect($scope.metadata).toEqual(metadata);
  });

  it('should put an editing episode on the scope', function(){
    var episode = opalTestHelper.newEpisode($rootScope);
    mkController(episode)
    expect(episode.demographics[0].first_name).toBe("John");
  });

  it('should put referencedata on to the scope', function(){
    mkController();
    expect($scope.some).toBe("data");
    expect(referencedata.toLookuplists).toHaveBeenCalled();
  });

  it('should close the instance if the call back returns a string', function(){
    mkController();
    $scope.pathway.pathwayResult.resolve({redirect_url: "somewhere"});
    $scope.$apply();
    expect($window.location.href).toEqual("somewhere");
  });

  it('should close the instance if the call back is rejected', function(){
    mkController();
    $scope.pathway.pathwayResult.reject("done");
    $scope.$apply();
    expect($window.alert).toHaveBeenCalledWith("unable to save patient");
  });
});
