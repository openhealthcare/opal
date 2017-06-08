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

        describe('can_see_pid', function() {

            it('should be true when we have none of the scary roles', function() {
                expect(profile.can_see_pid()).toBe(true);
            });

            it('should be false when researcher', function() {
                profile.roles['default'] = ['researcher']
                expect(profile.can_see_pid()).toBe(false);
            });

            it('should be false when scientist', function() {
                profile.roles['default'] = ['scientist']
                expect(profile.can_see_pid()).toBe(false);
            });

        });

        describe('can_edit', function() {

            it('should be true by default', function() {
                expect(profile.can_edit('demographics')).toBe(true);
            });

            it('should be false when a scientist and given an arbitrary record name', function() {
                profile.roles['default'] = ['scientist'];
                expect(profile.can_edit('demographics')).toBe(false);
            });

            it('should be true when a scientist given the right name', function() {
                profile.roles['default'] = ['scientist'];
                expect(profile.can_edit('lab_test')).toBe(true);
            });

        });

    });

});
