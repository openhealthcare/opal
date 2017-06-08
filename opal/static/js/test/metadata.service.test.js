describe('Metadata', function(){
    "use strict"

    var $httpBackend, $rootScope, $log;
    var mock, Metadata;
    var metadata = {
        foo: 'bar'
    };

    beforeEach(function(){
        mock = { alert: jasmine.createSpy() };

        module('opal.services', function($provide) {
            $provide.value('UserProfile', {
              load: function(){ return profile; }
            });
        });

        module(function($provide){
            $provide.value('$window', mock);
        });

        $log = jasmine.createSpyObj(['warn']);

        inject(function($injector){
            Metadata       = $injector.get('Metadata');
            $httpBackend   = $injector.get('$httpBackend');
            $rootScope     = $injector.get('$rootScope');
            $log = $injector.get('$log');
        });
        spyOn($log, "warn");
    });

    afterEach(function(){
      $httpBackend.verifyNoOutstandingExpectation();
      $httpBackend.verifyNoOutstandingRequest();
    });

    it('should fetch the metadata', function(){
        var result

        $httpBackend.whenGET('/api/v0.1/metadata/').respond(metadata);

        Metadata.load().then(function(r){ result = r; });

        $rootScope.$apply();
        $httpBackend.flush();

        expect(result.get('foo')).toEqual('bar');
    });

    it('should alert if the HTTP request errors', function(){
        var result;

        $httpBackend.whenGET('/api/v0.1/metadata/').respond(500, 'NO');
        Metadata.load();
        $rootScope.$apply();
        $httpBackend.flush();

        expect(mock.alert).toHaveBeenCalledWith('Metadata could not be loaded');
    });
});
