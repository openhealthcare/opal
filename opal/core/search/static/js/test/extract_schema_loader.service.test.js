describe('ExtractSchemaLoader', function() {
    "use strict";

    var $httpBackend, $q, $rootScope;
    var columns, $window;
    var mock, extractSchemaLoader;

    beforeEach(function() {
      module('opal');

      inject(function($injector){
        extractSchemaLoader = $injector.get('extractSchemaLoader');
        $httpBackend       = $injector.get('$httpBackend');
        $rootScope         = $injector.get('$rootScope');
        $q                 = $injector.get('$q');
        $window            = $injector.get('$window');
      });

      columns = {
          'demographics': {
              name: "demographics",
              fields: [
                  {name: 'first_name', type: 'string'},
                  {name: 'surname', type: 'string'},
                  {name: 'date_of_birth', type: 'date'},
              ]
        }
      };


      spyOn($window, "alert");
    });

    it('should fetch the schema', function(){
      var result;

      $httpBackend.whenGET('/search/api/extract/').respond(columns);
      extractSchemaLoader.then(
          function(r){ result = r; }
      );
      $rootScope.$apply();
      $httpBackend.flush();

      expect(!!result.columns).toEqual(true);
    });

    it('should alert if the http request errors', function(){
      var result;
      $httpBackend.whenGET('/search/api/extract/').respond(500, 'NO');
      extractSchemaLoader.then( function(r){ result = r; } );
      $rootScope.$apply();
      $httpBackend.flush();

      expect($window.alert).toHaveBeenCalledWith(
        'Extract schema could not be loaded'
      );
    });
});
