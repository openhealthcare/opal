describe('UserProfile', function(){
    "use strict";

    var mock, $httpBackend, $window, $routeParams, $log;
    var UserProfile, $q, $rootScope;
    var profile_data = {
        roles: {
            default: ['doctor', 'consultant'],
            tropical: ['oncall']
        }
    }

    beforeEach(function(){
        module('opal.services');

        mock = { alert: jasmine.createSpy() };
        inject(function($injector){
            UserProfile    = $injector.get('UserProfile');
            $q             = $injector.get('$q');
            $httpBackend   = $injector.get('$httpBackend');
            $rootScope     = $injector.get('$rootScope');
            $window        = $injector.get('$window');
            $routeParams   = $injector.get('$routeParams');
            $log = $injector.get('$log');
        });
        spyOn($log, "warn");
    });

    it('should alert if the HTTP request errors', function(){
        UserProfile.load();
        $httpBackend.expectGET('/api/v0.1/userprofile/').respond(500, 'NO');
        spyOn($window, 'alert');

        $rootScope.$apply();
        $httpBackend.flush();

        expect($window.alert).toHaveBeenCalledWith('UserProfile could not be loaded');
    });

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    describe('valid requests', function() {
        var profile

        beforeEach(function(){
            $httpBackend.expectGET('/api/v0.1/userprofile/').respond(profile_data);
            UserProfile.load().then(function(r){profile = r});
            $rootScope.$apply();
            $httpBackend.flush();
        });

        describe('active_roles()', function() {

            it('should return the roles', function() {
                expect(profile.active_roles()).toEqual(['doctor', 'consultant']);
            });

            it('should understand slug roles', function() {
                $routeParams.slug = 'tropical';
                expect(profile.active_roles()).toEqual(['doctor', 'consultant', 'oncall']);
            });

        });

        describe('has_role()', function() {

            it('should be true when we have the role', function() {
                expect(profile.has_role('doctor')).toBe(true);
            });

        });

    });

});
