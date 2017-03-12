describe('Referencedata', function(){
    "use strict"

    var $httpBackend, $rootScope, $log;
    var mock, Referencedata;
    var referencedata = {
        foo: ['bar']
    };

    beforeEach(function(){
        mock = { alert: jasmine.createSpy() };

        module('opal.services', function($provide) {
            $provide.value('UserProfile', {
              load: {
                then: function(fn){ return fn(profile); }
              }
            });
        });

        module(function($provide){
            $provide.value('$window', mock);
        });

        inject(function($injector){
            Referencedata  = $injector.get('Referencedata');
            $httpBackend   = $injector.get('$httpBackend');
            $rootScope     = $injector.get('$rootScope');
            $log = $injector.get('$log');
        });
        spyOn($log, "warn");
    });

    it('then should call through to load', function(){
        spyOn(Referencedata, "load").and.callThrough();
        var result;
        $httpBackend.whenGET('/api/v0.1/referencedata/').respond(referencedata);
        Referencedata.then(function(r){ result = r; });
        $rootScope.$apply();
        $httpBackend.flush();
        expect(result.get('foo')).toEqual(['bar']);
        expect($log.warn).toHaveBeenCalledWith(
          'This API is being deprecated and will be removed in 0.9.0. Please use Referencedata.load()'
        );
    });

    it('should fetch the referencedata', function(){
        var result;

        $httpBackend.whenGET('/api/v0.1/referencedata/').respond(referencedata);
        Referencedata.load().then(function(r){ result = r; });
        $rootScope.$apply();
        $httpBackend.flush();

        expect(result.get('foo')).toEqual(['bar']);
    });

    it('should alert if the HTTP request errors', function(){
        var result;

        $httpBackend.whenGET('/api/v0.1/referencedata/').respond(500, 'NO');
        Referencedata.load();
        $rootScope.$apply();
        $httpBackend.flush();

        expect(mock.alert).toHaveBeenCalledWith('Referencedata could not be loaded');
    });

    it('should return with the _list suffix', function(){
        var result

        $httpBackend.whenGET('/api/v0.1/referencedata/').respond(referencedata);

        Referencedata.load().then(function(r){ result = r; });
        $rootScope.$apply();
        $httpBackend.flush();
        expect(result.toLookuplists()).toEqual({foo_list: ['bar']});
    });

});
