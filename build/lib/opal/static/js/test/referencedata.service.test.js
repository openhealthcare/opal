describe('Referencedata', function(){
    "use strict"

    var $httpBackend, $rootScope, $log;
    var mock, Referencedata;
    var referencedata = {
        foo: ['bar']
    };

    beforeEach(function(){
        mock = { alert: jasmine.createSpy() };

        module('opal.services');

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
