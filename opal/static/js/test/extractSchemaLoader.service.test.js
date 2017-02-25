describe('services', function() {
    "use strict";

    var $httpBackend, $q, $rootScope;
    var columns, $window;

    var profile = {
        readonly   : false,
        can_extract: true,
        can_see_pid: function(){return true; }
    };

    beforeEach(function() {
        module('opal');
        columns = {
            "fields": {
                'demographics': {
                    name: "demographics",
                    single: true,
                    fields: [
                        {name: 'first_name', type: 'string'},
                        {name: 'surname', type: 'string'},
                        {name: 'date_of_birth', type: 'date'},
                    ]
                },
                "diagnosis": {
                    name: "diagnosis",
                    single: false,
                    sort: 'date_of_diagnosis',
                    fields: [
                        {name: 'date_of_diagnosis', type: 'date'},
                        {name: 'condition', type: 'string'},
                        {name: 'provisional', type: 'boolean'},
                    ]
                }
            }
        };
    });

    describe('extractSchemaLoader', function(){
        var mock, extractSchemaLoader;

        beforeEach(function(){
            inject(function($injector){
                extractSchemaLoader = $injector.get('extractSchemaLoader');
                $httpBackend       = $injector.get('$httpBackend');
                $rootScope         = $injector.get('$rootScope');
                $q                 = $injector.get('$q');
                $window            = $injector.get('$window');
            });

            spyOn($window, "alert");
        });

        it('should fetch the schema', function(){
            var result;

            $httpBackend.whenGET('/api/v0.1/extract-schema/').respond(columns);
            extractSchemaLoader.then(
                function(r){ result = r; }
            );
            $rootScope.$apply();
            $httpBackend.flush();

            expect(result.columns).toEqual(columns);
        });

        it('should alert if the http request errors', function(){
            var result;
            $httpBackend.whenGET('/api/v0.1/extract-schema/').respond(500, 'NO');
            extractSchemaLoader.then( function(r){ result = r; } );
            $rootScope.$apply();
            $httpBackend.flush();

            expect($window.alert).toHaveBeenCalledWith(
                'Extract schema could not be loaded');
        });
    });
});
