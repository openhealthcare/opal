describe('services', function() {
    "use strict";

    var columns, episodeData, options, records, list_schema, mockWindow;

    var profile = {
        readonly   : false,
        can_extract: true,
        can_see_pid: function(){return true; }
    };

    beforeEach(function(){
        module('opal', function($provide) {
            $provide.value('$analytics', function(){
                return {
                    pageTrack: function(x){}
                };
            });

            $provide.provider('$analytics', function(){
                this.$get = function() {
                    return {
                        virtualPageviews: function(x){},
                        settings: {
                            pageTracking: false,
                        },
                        pageTrack: function(x){}
                     };
                };
            });

        });

    });

    beforeEach(function() {
        columns = {
            "fields": {
                'demographics': {
                    name: "demographics",
                    single: true,
                    fields: [
                        {name: 'name', type: 'string'},
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
                name: 'John Smith',
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
        options =  {
            travel_reason: [
                "British Armed Forces",
                "Business",
                "Child visiting family",
                "Civilian sea/air crew",
                "Foreign Student",
                "Foreign Visitor",
                "Holiday",
                "Migrant",
                "Military",
                "New Entrant to UK",
                "Professional",
                "Tourism",
                "UK Citizen Living Abroad",
                "VFR",
                "Visiting Friends and Relatives",
                "Work"
            ]
        }
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

    describe('Schema', function() {
        var Schema, schema;

        beforeEach(function() {
            module('opal.services', function($provide) {
                $provide.value('UserProfile', function(){ return profile; });
            });

            inject(function($injector) {
                Schema = $injector.get('Schema');
            });
            schema = new Schema(_.values(columns.fields));
        });

        it('should be able to get the number of columns', function() {
            expect(schema.getNumberOfColumns()).toBe(2);
        });

        it('should be able to get a column', function() {
            expect(schema.getColumn('diagnosis').name).toBe('diagnosis');
        });

        it('should know whether a column is a singleton', function() {
            expect(schema.isSingleton('demographics')).toBe(true);
            expect(schema.isSingleton('diagnosis')).toBe(false);
        });
    });

    describe('Options', function(){
        var mock, Options;

        beforeEach(function(){
            mock = { alert: jasmine.createSpy() };

            module(function($provide){
                $provide.value('$window', mock);
            });

            inject(function($injector){
                Options        = $injector.get('Options');
                $q             = $injector.get('$q');
                $httpBackend   = $injector.get('$httpBackend');
                $rootScope     = $injector.get('$rootScope');
            });
        });

        it('should fetch the options', function(){
            var result

            $httpBackend.whenGET('/api/v0.1/options/').respond(options);

            Options.then(function(r){ result = r; });

            $rootScope.$apply();
            $httpBackend.flush();

            expect(result).toEqual(options);
        });

        it('should alert if the HTTP request errors', function(){
            var result;

            $httpBackend.whenGET('/api/v0.1/options/').respond(500, 'NO');

            $rootScope.$apply();
            $httpBackend.flush();

            expect(mock.alert).toHaveBeenCalledWith('Options could not be loaded');
        });
    });

    describe('episodesLoader', function(){
        var mock, episodesLoader, $route;

        beforeEach(function(){
            mock = { alert: jasmine.createSpy() };

            module(function($provide){
                $provide.value('$window', mock);
            });

            module('opal.services', function($provide) {
                $provide.value('UserProfile', function(){ return profile; });
            });

            inject(function($injector){
                episodesLoader = $injector.get('episodesLoader');
                $q             = $injector.get('$q');
                $httpBackend   = $injector.get('$httpBackend');
                $rootScope     = $injector.get('$rootScope');
                $route         = $injector.get('$route');
                Episode        = $injector.get('Episode');
                Schema         = $injector.get('Schema');
            });
            schema = new Schema(columns);
            $route.current = {params: {tag: 'micro'}};
        });

        it('should fetch the episodes', function(){
            var result

            $httpBackend.whenGET('/api/v0.1/record/').respond(records);
            $httpBackend.whenGET('/episode/micro').respond([episodeData]);

            episodesLoader().then(function(r){ result = r; });

            $rootScope.$apply();
            $httpBackend.flush();

            expect(result[123].demographics[0].name).toBe('John Smith');
            expect(result[123].demographics[0].date_of_birth).toEqual(
                new Date(1980, 6, 31));
        });

        it('should alert if the HTTP request errors', function(){
            var result;

            $httpBackend.whenGET('/api/v0.1/record/').respond(records);
            $httpBackend.whenGET('/episode/micro').respond(500, 'NO');
            episodesLoader();
            $rootScope.$apply();
            $httpBackend.flush();

            expect(mock.alert).toHaveBeenCalledWith('Episodes could not be loaded');
        });
    });

    describe('episodeVisibility', function(){
        var $scope, episode, episodeVisibility;

        beforeEach(function(){

            module('opal.services', function($provide) {
                $provide.value('UserProfile', function(){ return profile; });
            });

            inject(function($injector){
                episodeVisibility = $injector.get('episodeVisibility');
            });

            $scope = {
                currentTag: 'micro',
                currentSubTag: 'all',
                query: {
                    hospital_number: '',
                    ward: ''
                }
            }
            episode = episodeData;
        });
        it('should allow inactive episodes on mine', function(){
            episode.active = false;
            $scope.currentTag = 'mine';
            expect(episodeVisibility(episode, $scope)).toBe(true);
        });
        it('should allow inactive episodes', function(){
            episode.active = false;
            expect(episodeVisibility(episode, $scope)).toBe(true);
        });
        it('should reject if the hospital number filter fails', function(){
            $scope.currentTag = 'tropical';
            $scope.query.hospital_number = '123'
            expect(episodeVisibility(episode, $scope)).toBe(false);
        });
        it('should allow if the hospital number filter passes', function(){
            $scope.currentTag = 'tropical';
            expect(episodeVisibility(episode, $scope)).toBe(true);
        });
        it('should reject if the name filter fails', function(){
            $scope.currentTag = 'tropical';
            $scope.query.name = 'Fake Name';
            expect(episodeVisibility(episode, $scope)).toBe(false);
        });
        it('should allow if the name filter passes', function(){
            $scope.currentTag = 'tropical';
            $scope.query.name = 'john'
            expect(episodeVisibility(episode, $scope)).toBe(true);
        });
        it('should allow if unfiltered', function(){
            expect(episodeVisibility(episode, $scope)).toBe(true);
        });
        it('should allow if the bed filter passes', function(){
            $scope.query.bed = '15'
            expect(episodeVisibility(episode, $scope)).toBe(true);
        });
        it('should allow if the bed rangefilter passes', function(){
            $scope.query.bed = '10-20'
            expect(episodeVisibility(episode, $scope)).toBe(true);
        });
        it('should fail if the bed filter fails', function(){
            $scope.query.bed = '14'
            expect(episodeVisibility(episode, $scope)).toBe(false);
        });
        it('should fail if the bed range filter fails', function(){
            $scope.query.bed = '1-10'
            expect(episodeVisibility(episode, $scope)).toBe(false);
        });

    });

    describe('episodesLoader', function() {
        var episodesLoader, $httpBackend, listSchemaLoader, $route;

        beforeEach(function() {
            module(function($provide) {
                $provide.value('UserProfile', function(){ return profile; });
            });

            inject(function($injector) {
                episodesLoader   = $injector.get('episodesLoader');
                $route           = $injector.get('$route');
                $httpBackend     = $injector.get('$httpBackend');
                $rootScope       = $injector.get('$rootScope');
            });
            $route.current = {params: {tag: 'micro'}};
        });

        it('should resolve to an object of episodes', function() {
            var promise = episodesLoader();
            var episodes;
            $httpBackend.whenGET('/api/v0.1/record/').respond(records);
            // TODO trailing slash?
            $httpBackend.whenGET('/episode/micro').respond([episodeData]);
            promise.then(function(value) {
                episodes = value;
            });

            $httpBackend.flush();
            $rootScope.$apply();

            expect(episodes[123].id).toBe(123);
        });
    });

    describe('episodeLoader', function() {
        var episodeLoader, $httpBackend;

        beforeEach(function() {
            module(function($provide) {
                $provide.value('UserProfile', function(){ return profile; });
            });

            inject(function($injector) {
                episodeLoader = $injector.get('episodeLoader');
                $httpBackend = $injector.get('$httpBackend');
                $rootScope = $injector.get('$rootScope');
                $route = $injector.get('$route');
            });
        });

        xit('should resolve to a single episode', function() {
            // TODO unskip this
            // Skipping this, because I can't work out how to set $route.current
            // so that episodeLoader can access it.
            var promise = episodeLoader();
            var episode;

            $route.current = {params: {id: 123}};
            $httpBackend.whenGET('/schema/').respond(columns);
            // TODO trailing slash?
            $httpBackend.whenGET('/episode/123').respond(episodeData);
            promise.then(function(value) {
                episode = value;
            });

            $httpBackend.flush();
            $rootScope.$apply();

            expect(episode.id).toBe(123);
        });
    });

    describe('UserProfile', function(){
        var mock, $httpBackend, UserProfile;

        beforeEach(function(){
            mock = { alert: jasmine.createSpy() };

            module(function($provide){
                $provide.value('$window', mock);
            });

            inject(function($injector){
                UserProfile    = $injector.get('UserProfile');
                $q             = $injector.get('$q');
                $httpBackend   = $injector.get('$httpBackend');
                $rootScope     = $injector.get('$rootScope');
            });
        });

        it('should alert if the HTTP request errors', function(){
            var result;

            $httpBackend.expectGET('/api/v0.1/userprofile/');
            $httpBackend.whenGET('/api/v0.1/userprofile/').respond(500, 'NO');

            $rootScope.$apply();
            $httpBackend.flush();

            expect(mock.alert).toHaveBeenCalledWith('UserProfile could not be loaded');
        });
    });


});
