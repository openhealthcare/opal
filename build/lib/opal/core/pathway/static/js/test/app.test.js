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

    describe('/:pathway/:patient_id?/:episode_id?', function() {
      it('should resolve with episode id', function() {
          var fakeRoute = {current: {params: {patient_id: 1, episode_id: 1}}};
          eLoader.and.returnValue('episode');
          var routed = $route.routes['/:pathway/:patient_id?/:episode_id?'];
          var resolve = routed.resolve;
        expect(resolve.episode(fakeRoute, eLoader)).toEqual('episode');
          expect(eLoader).toHaveBeenCalledWith(1);
          expect(resolve.metadata(metadata)).toBe("some metadata");
          expect(resolve.referencedata(referencedata)).toBe("some reference data");
          expect(resolve.recordLoader(recordLoader)).toEqual("some record data");
          expect(resolve.pathwayDefinition(fakeRoute, pathwayLoader)).toBe("some pathway");
          var route = {current: {params: {pathway: "somePathway"}}};
          expect(resolve.pathwayName(route)).toBe('somePathway');
          expect(routed.templateUrl({pathway: "something"})).toBe("/pathway/templates/something.html");
      });

      it('should resolve without an episode id', function(){
        var fakeRoute = {current: {params: {}}};
        var routed = $route.routes['/:pathway/:patient_id?/:episode_id?'];
        var resolve = routed.resolve;
        var result = resolve.episode(fakeRoute, eLoader);
        expect(eLoader).not.toHaveBeenCalled();
        expect(result).toBe(undefined);
      });
    });
});
