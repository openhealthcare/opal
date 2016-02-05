describe('services', function() {
    var columns, episodeData, options, records, list_schema, mockWindow;

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
            },
            "list_schema": {
                "default": [
                    'demographics',
                    'diagnosis'
                ]
            }
        };

        records = columns.fields;
        list_schema  = columns.list_schema;

        episodeData = {
            id: 123,
            date_of_admission: "2013-11-19",
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
                date_of_birth: '1980-07-31',
                hospital_number: '555'
            }],
            location: [{
                category: 'Inepisode',
                hospital: 'UCH',
                ward: 'T10',
                bed: '15',
                date_of_admission: '2013-08-01',
            }],
            diagnosis: [{
                id: 102,
                condition: 'Dengue',
                provisional: true,
                date_of_diagnosis: '2007-04-20'
            }, {
                id: 103,
                condition: 'Malaria',
                provisional: false,
                date_of_diagnosis: '2006-03-19'
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

    describe('listSchemaLoader', function(){
        var mock;

        beforeEach(function(){
            $window = {alert: jasmine.createSpy() };

            module(function($provide) {
              $provide.value('$window', $window);
            });

            inject(function($injector){
                listSchemaLoader = $injector.get('listSchemaLoader');
                Schema           =  $injector.get('Schema');
                $httpBackend     = $injector.get('$httpBackend');
                $rootScope       = $injector.get('$rootScope');
                $q               = $injector.get('$q');
                $route           = $injector.get('$route');
                mockWindow = $injector.get('$window');
            });
            $route.current = {params: {tag: 'micro'}};
            $httpBackend.whenGET('/api/v0.1/record/').respond(records);
        });

        it('should fetch the schema', function(){
            var result

            $httpBackend.whenGET('/api/v0.1/list-schema/').respond(list_schema);
            listSchemaLoader().then(
                function(r){ result = r}
            );
            $rootScope.$apply();
            $httpBackend.flush();

            expect(result.columns).toEqual(_.values(columns.fields));
        });

        it('should alert if the http request errors', function(){
            var result

            $httpBackend.whenGET('/api/v0.1/list-schema/').respond(500, 'NO');

            listSchemaLoader().then( function(r){ result = r } );
            $rootScope.$apply();
            $httpBackend.flush()

            expect(mockWindow.alert).toHaveBeenCalledWith('List schema could not be loaded');
        });

        it('should provide the default schema on a sublist', function(){
            $route.current.params.subtag = 'micro_haem';

            var mycols = angular.copy(list_schema);
            mycols.micro = {};
            mycols.micro.default = mycols.default

            $httpBackend.whenGET('/api/v0.1/list-schema/').respond(mycols);

            listSchemaLoader().then(function(r){result=r});
            $rootScope.$apply();
            $httpBackend.flush();
            expect(result.columns).toEqual(_.values(columns.fields));
        });
    })

    describe('extractSchemaLoader', function(){
        var mock;

        beforeEach(function(){
            mock = { alert: jasmine.createSpy() };

            module(function($provide) {
                $provide.value('$window', mock);
            });

            inject(function($injector){
                extractSchemaLoader = $injector.get('extractSchemaLoader');
                Schema             =  $injector.get('Schema');
                $httpBackend       = $injector.get('$httpBackend');
                $rootScope         = $injector.get('$rootScope');
                $q                 = $injector.get('$q');
            });
        });

        it('should fetch the schema', function(){
            var result

            $httpBackend.whenGET('/api/v0.1/extract-schema/').respond(columns);
            extractSchemaLoader.then(
                function(r){ result = r}
            );
            $rootScope.$apply();
            $httpBackend.flush();

            expect(result.columns).toEqual(columns);
        });

        it('should alert if the http request errors', function(){
            var result
            $httpBackend.whenGET('/api/v0.1/extract-schema/').respond(500, 'NO');
            extractSchemaLoader.then( function(r){ result = r } );
            $rootScope.$apply();
            $httpBackend.flush()

            expect(mock.alert).toHaveBeenCalledWith(
                'Extract schema could not be loaded');
        });
    });

    describe('Schema', function() {
        var Schema, schema;

        beforeEach(function() {
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
        var mock;

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
        var mock;

        beforeEach(function(){
            mock = { alert: jasmine.createSpy() };

            module(function($provide){
                $provide.value('$window', mock);
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
            $httpBackend.whenGET('/api/v0.1/list-schema/').respond(columns);
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
        var $scope, episode;

        beforeEach(function(){
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
            expect(episodeVisibility(episode, $scope, false)).toBe(true);
        });
        it('should reject inactive episodes', function(){
            episode.active = false;
            expect(episodeVisibility(episode, $scope, false)).toBe(false);
        });
        it('should reject if the current tag is not true', function(){
            expect(episodeVisibility(episode, $scope, false)).toBe(false);
        });
        it('should reject if the current subtag is not true', function(){
            $scope.currentTag = 'tropical';
            $scope.currentSubTag = 'tropical_outpatients';
            expect(episodeVisibility(episode, $scope, false)).toBe(false);
        });
        it('should reject if the hospital number filter fails', function(){
            $scope.currentTag = 'tropical';
            $scope.query.hospital_number = '123'
            expect(episodeVisibility(episode, $scope, false)).toBe(false);
        });
        it('should allow if the hospital number filter passes', function(){
            $scope.currentTag = 'tropical';
            expect(episodeVisibility(episode, $scope, false)).toBe(true);
        });
        it('should reject if the name filter fails', function(){
            $scope.currentTag = 'tropical';
            $scope.query.name = 'Fake Name';
            expect(episodeVisibility(episode, $scope, false)).toBe(false);
        });
        it('should allow if the name filter passes', function(){
            $scope.currentTag = 'tropical';
            $scope.query.name = 'john'
            expect(episodeVisibility(episode, $scope, false)).toBe(true);
        });
        it('should allow if in the tag & unfiltered', function(){
            $scope.currentTag = 'tropical';
            expect(episodeVisibility(episode, $scope, false)).toBe(true);
        })
    });


    describe('Item', function() {
        var Item, item;
        var mockEpisode = {
            addItem: function(item) {},
            removeItem: function(item) {},
            demographics: [{name: 'Name'}]
        };

        beforeEach(function() {
            inject(function($injector) {
                Item = $injector.get('Item');
            });

            item = new Item(episodeData.demographics[0], mockEpisode, columns.fields.demographics);
        });

        it('should have correct attributes', function() {
            expect(item.id).toBe(101)
            expect(item.name).toBe('John Smith');

        });

        it('should convert values of date fields to Date objects', function() {
            expect(item.date_of_birth).toEqual(new Date(1980, 6, 31));
        });

        it('should be able to produce copy of attributes', function() {
            expect(item.makeCopy()).toEqual({
                id: 101,
                name: 'John Smith',
                date_of_birth: '31/07/1980',
            });
        });

        describe('communicating with server', function() {
            var $httpBackend, item;

            beforeEach(function() {
                inject(function($injector) {
                    $httpBackend = $injector.get('$httpBackend');
                });
            });

            afterEach(function() {
                $httpBackend.verifyNoOutstandingExpectation();
                $httpBackend.verifyNoOutstandingRequest();
            });

            describe('saving existing item', function() {
                var attrsWithJsonDate, attrsWithHumanDate;

                beforeEach(function() {
                    attrsWithJsonDate = {
                        id: 101,
                        name: 'John Smythe',
                        date_of_birth: '1980-07-30',
                    };
                    attrsWithHumanDate = {
                        id: 101,
                        name: 'John Smythe',
                        date_of_birth: '30/07/1980',
                    };
                    item = new Item(episodeData.demographics[0],
                                    mockEpisode,
                                    columns.fields.demographics);
                    $httpBackend.whenPUT('/api/v0.1/demographics/101/')
                        .respond(attrsWithJsonDate);
                });

                it('should hit server', function() {
                    $httpBackend.expectPUT('/api/v0.1/demographics/101/', attrsWithJsonDate);
                    item.save(attrsWithHumanDate);
                    $httpBackend.flush();
                });

                it('should update item attributes', function() {
                    item.save(attrsWithHumanDate);
                    $httpBackend.flush();
                    expect(item.id).toBe(101);
                    expect(item.name).toBe('John Smythe');
                    expect(item.date_of_birth).toEqual(new Date(1980, 6, 30));
                });

            });

            describe('saving new item', function() {
                var attrs;

                beforeEach(function() {
                    attrs = {id: 104, condition: 'Ebola', provisional: false};
                    item = new Item({}, mockEpisode, columns.fields.diagnosis);
                    $httpBackend.whenPOST('/api/v0.1/diagnosis/').respond(attrs);
                });

                it('should hit server', function() {
                    $httpBackend.expectPOST('/api/v0.1/diagnosis/');
                    item.save(attrs);
                    $httpBackend.flush();
                });

                it('should set item attributes', function() {
                    item.save(attrs);
                    $httpBackend.flush();
                    expect(item.id).toBe(104);
                    expect(item.condition).toBe('Ebola');
                    expect(item.provisional).toBe(false);
                });

                it('should notify episode', function() {
                    spyOn(mockEpisode, 'addItem');
                    item.save(attrs);
                    $httpBackend.flush();
                    expect(mockEpisode.addItem).toHaveBeenCalled();
                });
            });

            describe('deleting item', function() {
                beforeEach(function() {
                    item = new Item(episodeData.diagnosis[1], mockEpisode, columns.fields.diagnosis);
                    $httpBackend.whenDELETE('/api/v0.1/diagnosis/103/').respond();
                });

                it('should hit server', function() {
                    $httpBackend.expectDELETE('/api/v0.1/diagnosis/103/');
                    item.destroy();
                    $httpBackend.flush();
                });

                it('should notify episode', function() {
                    spyOn(mockEpisode, 'removeItem');
                    item.destroy();
                    $httpBackend.flush();
                    expect(mockEpisode.removeItem).toHaveBeenCalled();
                });
            });
        });
    });

    describe('episodesLoader', function() {
        var episodesLoader, $httpBackend;

        beforeEach(function() {
            inject(function($injector) {
                listSchemaLoader = $injector.get('listSchemaLoader');
                episodesLoader   = $injector.get('episodesLoader');
                $route           = $injector.get('$route');
                $httpBackend     = $injector.get('$httpBackend');
                $rootScope       = $injector.get('$rootScope');
            });
            $route.current = {params: {tag: 'micro'}}
        });

        it('should resolve to an object of episodes', function() {
            var promise = episodesLoader();
            var episodes;
            $httpBackend.whenGET('/api/v0.1/record/').respond(records);
            $httpBackend.whenGET('/api/v0.1/list-schema/').respond(list_schema);
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
        var mock, $httpBackend;

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
