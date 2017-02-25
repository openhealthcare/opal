describe('services', function() {
    "use strict";

    var $httpBackend, $q, $rootScope;
    var columns, episodeData, records, list_schema, mockWindow;

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

        records = columns.fields;

        episodeData = {
            id: 123,
            date_of_admission: "19/11/2013",
            active: true,
            discharge_date: null,
            date_of_episode: null,
            tagging: [{
                mine: true,
                tropical: true
                }],
            demographics: [{
                id: 101,
                first_name: 'John',
                surname: 'Smith',
                date_of_birth: '31/071980',
                hospital_number: '555'
            }],
            location: [{
                category: 'Inepisode',
                hospital: 'UCH',
                ward: 'T10',
                bed: '15',
                date_of_admission: '01/08/2013',
            }],
            diagnosis: [{
                id: 102,
                condition: 'Dengue',
                provisional: true,
                date_of_diagnosis: '20/04/2007'
            }, {
                id: 103,
                condition: 'Malaria',
                provisional: false,
                date_of_diagnosis: '19/03/2006'
            }]
        };
    });

    describe('extractSchemaLoader', function(){
        var mock, extractSchemaLoader;

        beforeEach(function(){
            mock = { alert: jasmine.createSpy() };

            module(function($provide) {
                $provide.value('$window', mock);
            });

            module('opal.services', function($provide) {
                $provide.value('UserProfile', function(){ return profile; });
            });

            inject(function($injector){
                extractSchemaLoader = $injector.get('extractSchemaLoader');
                $httpBackend       = $injector.get('$httpBackend');
                $rootScope         = $injector.get('$rootScope');
                $q                 = $injector.get('$q');
            });
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

            expect(mock.alert).toHaveBeenCalledWith(
                'Extract schema could not be loaded');
        });
    });
});
