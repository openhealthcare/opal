describe('User', function(){
    "use strict";

    var $httpBackend, $rootScope;
    var mock_window;
    var User;
    var userdata = {
        'readonly'   : false,
        'can_extract': false,
        'filters'    : [],
        'roles'      : {'default': []},
        'full_name'  : 'Jane Doe',
        'avatar_url' : 'http://gravatar.com/avatar/5d9c68c6c50ed3d02a2fcf54f63993b6?s=80&r=g&d=identicon',
        'user_id'    : 1
    };


    beforeEach(function(){
        module('opal.services');

        mock_window = { alert: jasmine.createSpy() };

        module(function($provide){
            $provide.value('$window', mock_window);
        });

        inject(function($injector){
            $httpBackend = $injector.get('$httpBackend');
            $rootScope   = $injector.get('$rootScope');
            User         = $injector.get('User');
        });
    });

    afterEach(function(){
      $httpBackend.verifyNoOutstandingExpectation();
      $httpBackend.verifyNoOutstandingRequest();
    });

    describe('all()', function() {

        it('should fetch a list of users', function() {
            $httpBackend.whenGET('/api/v0.1/user/').respond([userdata]);
            User.all().then(function(users){
                expect(users.length).toEqual(1);
                expect(users[0].full_name).toEqual('Jane Doe');
            });
            $httpBackend.flush();
            $rootScope.$apply();
        });

        it('should alert if we error', function() {
            $httpBackend.whenGET('/api/v0.1/user/').respond(500, 'NO');
            User.all();
            $httpBackend.flush();
            $rootScope.$apply();
            expect(mock_window.alert).toHaveBeenCalledWith('Users could not be loaded')
        });

    });

    describe('get()', function() {

        it('should fetch a list of users', function() {
            $httpBackend.whenGET('/api/v0.1/user/1/').respond(userdata);
            User.get(1).then(function(user){
                expect(user.full_name).toEqual('Jane Doe');
            });
            $httpBackend.flush();
            $rootScope.$apply();
        });

        it('should alert if we error', function() {
            $httpBackend.whenGET('/api/v0.1/user/2/').respond(404, 'NO');
            User.get(2);
            $httpBackend.flush();
            $rootScope.$apply();
            expect(mock_window.alert).toHaveBeenCalledWith('User could not be loaded')
        });

    });


});
