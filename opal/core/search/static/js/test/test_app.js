describe('app', function() {
    "use strict";

    var $route;
    var profile;
    var extractSchema;
    var referencedata;
    var filters;

    beforeEach(function(){
      module('opal.search');
      profile = {load: function(){}};
      extractSchema = {load: function(){}};
      referencedata = {load: function(){}};
      filters = {load: function(){}};
      spyOn(profile, "load").and.returnValue("some profile");
      spyOn(extractSchema, "load").and.returnValue("some schema");
      spyOn(referencedata, "load").and.returnValue("some reference data");
      spyOn(filters, "load").and.returnValue("some filters");

      inject(function($injector){
        $route   = $injector.get('$route');
      });
    });

    describe('/extract', function() {
      it('should resolve with episode id', function() {
          var fakeRoute = {current: {params: {patient_id: 1, episode_id: 1}}};
          var routed = $route.routes['/extract'];
          var resolve = routed.resolve;
          expect(resolve.profile(profile)).toBe("some profile");
          expect(resolve.extractSchema(extractSchema)).toBe("some schema");
          expect(resolve.filters(filters)).toBe("some filters");
          expect(resolve.referencedata(referencedata)).toBe(
              "some reference data"
          );
      });
    });
});
