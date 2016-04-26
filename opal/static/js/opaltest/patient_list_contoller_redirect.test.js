describe('PatientListRedirectListCtrl', function() {
  "use strict";

  var $location, $cookieStore, $controller, $scope, $rootScope;
  var fakeOptions = {
      first_list_slug: 'carnivore-eater',
      tag_hierarchy: {
          "parentTag": [
              "childTag",
              "otherChildTag"
          ]
      }
  };

  var fakeOptionsPromise = {then: function(someFun){ return someFun(fakeOptions); }};

  beforeEach(module('opal.controllers'));
  beforeEach(inject(function($injector){
      $location    = $injector.get('$location');
      spyOn($location, 'path');
      $cookieStore = $injector.get('$cookieStore');
      $controller  = $injector.get('$controller');
      $rootScope   = $injector.get('$rootScope');
      $scope       = $rootScope.$new();
  }));

  it('should redirect to the cookie store list', function() {
      var $cookieStore = {
          get: function(someKey){
              if(someKey === 'opal.lastPatientList'){
                  return "cookietag"
              }
              throw "unknown argument " + someKey;
          }
      };

      $controller('PatientListRedirectCtrl', {
          $scope: $scope,
          $cookieStore: $cookieStore,
          $location: $location ,
          options: fakeOptions
      });
      expect($location.path).toHaveBeenCalledWith("/list/cookietag/");
  });


  it('should redirect to the first list slug if there is no tag', function(){
        spyOn($cookieStore, 'get').and.returnValue(undefined);
        $controller('PatientListRedirectCtrl', {
            $scope: $scope,
            $cookieStore: $cookieStore,
            $location: $location,
            options: fakeOptions
        });
        expect($location.path).toHaveBeenCalledWith("/list/carnivore-eater/");
        expect($cookieStore.get).toHaveBeenCalledWith("opal.lastPatientList");
    });

});
