describe('recordLoader', function(){
    "use strict"

    var $httpBackend, $rootScope, recordLoader;
    var mock;
    var recordSchema = {
        'demographics': {
            name: "demographics",
            single: true,
            fields: [
                {name: 'first_name', type: 'string'},
                {name: 'surname', type: 'string'},
                {name: 'date_of_birth', type: 'date'},
            ]
      }
    };

    beforeEach(function(){
        mock = { alert: jasmine.createSpy() };
        module('opal.services');

        module(function($provide){
            $provide.value('$window', mock);
        });

        inject(function($injector){
            recordLoader   = $injector.get('recordLoader');
            $httpBackend   = $injector.get('$httpBackend');
            $rootScope     = $injector.get('$rootScope');
        });
    });

    it('should fetch the record data', function(){
        var result;
        $httpBackend.whenGET('/api/v0.1/record/').respond(recordSchema);
        recordLoader.then(function(r){ result = r; });
        $rootScope.$apply();
        $httpBackend.flush();
        expect(result).toEqual(recordSchema);
        expect($rootScope.fields).toEqual(recordSchema);
    });

    it('should alert if the HTTP request errors', function(){
        var result;
        $httpBackend.whenGET('/api/v0.1/record/').respond(500, 'NO');
        $rootScope.$apply();
        $httpBackend.flush();
        expect(mock.alert).toHaveBeenCalledWith('Records could not be loaded');
    });
});
