//
// Unittests for the main OPAL router
//
describe('Routes', function() {
    "use strict";

    var $route;

    beforeEach(function(){
        module('opal');

        inject(function($injector){
            $route   = $injector.get('$route');
        });
    });

    describe('/list/', function() {
        it('should load Metadata', function() {
            var resolve = $route.routes['/list/'].resolve;
            expect(resolve.metadata('Metadata')).toBe('Metadata');
        });
    });

    describe('/list/:slug', function() {

        it('should resolve injected things', function() {
            var resolve = $route.routes['/list/:slug'].resolve;
            expect( resolve.episodedata( function(){ return {} } ) ).toEqual({});
            expect(resolve.metadata('Metadata')).toBe('Metadata');
            expect(resolve.profile('Profile')).toEqual('Profile');
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
            expect(resolve.profile('Profile')).toEqual('Profile');
            expect(resolve.metadata('Metadata')).toBe('Metadata');
        });

        it('should know the template', function() {
            var template = $route.routes['/patient/:patient_id/:view?'].templateUrl;
            expect(template()).toEqual('/templates/patient_detail.html');
        });

    });

    describe('/extract', function() {
        it('should resolve injected things', function() {
            var resolve = $route.routes['/extract'].resolve;
            expect(resolve.profile('Profile')).toEqual('Profile');
            expect(resolve.schema('Schema')).toEqual('Schema');
            expect(resolve.filters(function(){return {}})).toEqual({});
        });
    });

});
