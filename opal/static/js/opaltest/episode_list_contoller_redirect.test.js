describe('EpisodeRedirectListCtrl', function() {
  "use strict";

  var $location, $cookieStore, $controller, $scope;
  var fakeOptions = {
      tag_hierarchy: {
          "parentTag": [
              "childTag",
              "otherChildTag"
          ]
      }
  };

  beforeEach(module('opal.controllers'));
  beforeEach(inject(function($injector){
      $location    = $injector.get('$location');
      spyOn($location, 'path');
      $cookieStore = $injector.get('$cookieStore');
      $controller  = $injector.get('$controller');
      $rootScope   = $injector.get('$rootScope');
      $scope       = $rootScope.$new();
  }));

  it('should redirect to the cookie store tag and sub tag', function() {
      var $cookieStore = {
          get: function(someKey){
              if(someKey === "opal.currentTag"){
                  return "cookieTag";
              }
              if(someKey === "opal.currentSubTag"){
                  return "cookieSubTag";
              }

              throw "unknown argument " + someKey;
          }
      };
      $controller('EpisodeRedirectListCtrl', {
          $scope: $scope,
          $cookieStore: $cookieStore,
          $location: $location ,
          options: fakeOptions
      });
      expect($location.path).toHaveBeenCalledWith("/list/cookieTag/cookieSubTag");
  });

  it('should redirect to the options child tag second', function(){
    var $cookieStore = {
        get: function(someKey){
            if(someKey === "opal.currentTag"){
                return "parentTag";
            }
            if(someKey === "opal.currentSubTag"){
                return "";
            }

            throw "unknown argument " + someKey;
        }
    };
    $controller('EpisodeRedirectListCtrl', {
        $scope: $scope,
        $cookieStore: $cookieStore,
        $location: $location ,
        options: fakeOptions
    });
    expect($location.path).toHaveBeenCalledWith("/list/parentTag/childTag");
  });

  it('should redirect to the first option if there is no tag', function(){
        spyOn($cookieStore, 'get').and.returnValue(undefined);
        $controller('EpisodeRedirectListCtrl', {
            $scope: $scope,
            $cookieStore: $cookieStore,
            $location: $location ,
            options: fakeOptions
        });
        expect($location.path).toHaveBeenCalledWith("/list/parentTag/childTag");
        expect($cookieStore.get).toHaveBeenCalledWith("opal.currentTag");
        expect($cookieStore.get).toHaveBeenCalledWith("opal.currentSubTag");
  });
});
