//
// Unittests for the main OPAL router
//
describe('Routes', function() {
    "use strict";

    var $route;
    var metadata;
    var userProfile;
    var referencedata;

    beforeEach(function(){
        module('opal');
        metadata = {load: function(){}};
        userProfile = {load: function(){}};
        referencedata = {load: function(){}};
        spyOn(metadata, "load").and.returnValue("some metadata");
        spyOn(userProfile, "load").and.returnValue("some user profile");
        spyOn(referencedata, "load").and.returnValue("some reference data");

        inject(function($injector){
            $route   = $injector.get('$route');
        });
    });

    describe('/list/', function() {
        it('should load Metadata', function() {
            var resolve = $route.routes['/list/'].resolve;
            expect(resolve.metadata(metadata)).toBe("some metadata");
        });
    });

    describe('/list/:slug', function() {

        it('should resolve injected things', function() {
            var resolve = $route.routes['/list/:slug'].resolve;
            expect( resolve.episodedata( function(){ return {}; } ) ).toEqual({});
            expect(resolve.metadata(metadata)).toBe("some metadata");
            expect(resolve.profile(userProfile)).toEqual("some user profile");
        });

        it('should add the slug to the template url', function() {
            var templateUrl = $route.routes['/list/:slug'].templateUrl;
            expect(templateUrl({slug: 'my-slug'})).toEqual('/templates/patient_list.html/my-slug');
        });

    });

    describe('/patient/:patient_id/access_log', function() {
        it('should resolve the patient', function() {
            var resolve = $route.routes['/patient/:patient_id/access_log'].resolve;
            expect(resolve.patient(function(){return {}})).toEqual({});
        });
    });

    describe('/patient/:patient_id/:view?', function() {

        it('should resolve injected things', function() {
            var resolve = $route.routes['/patient/:patient_id/:view?'].resolve;
            expect(resolve.patient(function(){return {};})).toEqual({});
            expect(resolve.profile(userProfile)).toEqual("some user profile");
            expect(resolve.metadata(metadata)).toBe("some metadata");
        });

        it('should know the template', function() {
            var template = $route.routes['/patient/:patient_id/:view?'].templateUrl;
            expect(template()).toEqual('/templates/patient_detail.html');
        });

    });
});
