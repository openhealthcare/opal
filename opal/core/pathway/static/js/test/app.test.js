describe('app', function() {
    "use strict";

    var $route;
    var metadata;
    var recordLoader;
    var referencedata;
    var eLoader;
    var pathwayLoader;

    beforeEach(function(){
      module('opal.pathway');
      eLoader = jasmine.createSpy();
      metadata = {load: function(){}};
      recordLoader = {load: function(){}};
      referencedata = {load: function(){}};
      pathwayLoader = {load: function(){}};
      spyOn(metadata, "load").and.returnValue("some metadata");
      spyOn(recordLoader, "load").and.returnValue("some record data");
      spyOn(referencedata, "load").and.returnValue("some reference data");
      spyOn(pathwayLoader, "load").and.returnValue("some pathway");

      inject(function($injector){
        $route = $injector.get('$route');
      });
    });

    describe('/', function() {
      it('should not load anything for the redirection', function() {
          var routed = $route.routes['/'];
          expect(metadata.load).not.toHaveBeenCalled();
          expect(referencedata.load).not.toHaveBeenCalled();
          expect(eLoader).not.toHaveBeenCalled();
          expect(routed.templateUrl).toEqual("/templates/loading_page.html");
          expect(routed.controller).toEqual("PathwayRedirectCtrl");
      });
    });
});
