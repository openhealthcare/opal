describe('Episode', function() {
    "use strict";

    var Episode, EpisodeResource, Item, $scope, $rootScope, columns, $window;
    var episode, episodeData, resource, tag_hierarchy, fields;
    var $routeParams;

    beforeEach(function() {
        module('opal.services', function($provide) {
            $provide.value('UserProfile', {
              load: function(){ return profile; }
            });
        });

        tag_hierarchy = {
            'mine'    : [],
            'tropical': [],
            'micro'   : [
                'ortho', 'haem'
            ]
        };

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
                },
                microbiology_test: {
                    name: "microbiology_test",
                    single: false,
                    fields: [
                        {name: 'date_ordered', type: 'date'}
                    ]
                },
                general_note: {
                    name: 'general_note',
                    fields: [
                        {name: 'date', type: 'date'}
                    ]
                },
                microbiology_input: {
                    name: 'microbiology_input',
                    fields: [
                        {name: 'initials', type: 'string'},
                        {name: 'when', type: 'datetime'}
                    ]
                },
                antimicrobial: {
                    name: 'antimicrobial',
                    fields: [
                        {name: 'start_date', type: 'date'}
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

        episodeData = {
            id: 123,
            date_of_admission: "19/11/2013",
            category_name: 'inpatient',
            active: true,
            discharge_date: "25/05/2016",
            date_of_episode: "20/11/2013",
            start: "19/11/2013",
            end: "25/05/2016",
            tagging: [{
                mine: true,
                tropical: true
                }],
            demographics: [{
                id: 101,
                patient_id: 99,
                first_name: 'John',
                surname: "Smith",
                date_of_birth: '31/07/1980',
                hospital_number: '555'
            }],
            location: [{
                category: 'Inepisode',
                hospital: 'UCH',
                ward: 'T10',
                bed: '15',
                date_of_admission: '01/08/2013'
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
                date_of_diagnosis: '03/19/2006'
            }]
        };

        fields = {};
        _.each(columns.fields, function(c){
            fields[c.name] = c;
        });

        inject(function($injector) {
            Episode = $injector.get('Episode');
            Item = $injector.get('Item');
            $rootScope  = $injector.get('$rootScope');
            $scope      = $rootScope.$new();
            $routeParams = $injector.get('$routeParams');
            $window      = $injector.get('$window');
        });
        $rootScope.fields = fields;

        episode = new Episode(angular.copy(episodeData));
    });

    describe('initialisation', function() {

        it('should throw if there is no patient ID', function() {
            expect(function(){ new Episode({});}).toThrow();
        });

        it('should cast dates on the episode if appropriate', function(){
            var episodeDataCloned = angular.copy(episodeData);
            var newEpisode = new Episode(episodeDataCloned);
            expect(moment(newEpisode.date_of_admission).format('DD/MM/YYYY')).toEqual("19/11/2013");
            expect(moment(newEpisode.start).format('DD/MM/YYYY')).toEqual("19/11/2013");
            expect(moment(newEpisode.end).format('DD/MM/YYYY')).toEqual("25/05/2016");
            expect(moment(newEpisode.date_of_episode).format('DD/MM/YYYY')).toEqual("20/11/2013");
            expect(moment(newEpisode.discharge_date).format('DD/MM/YYYY')).toEqual("25/05/2016");
        });
    });

    it('should compare comparators that are different', function() {
        var datacopy = angular.copy(episodeData);
        datacopy.location[0].bed = '87';
        var first       = new Episode(episodeData);
        var second      = new Episode(datacopy);
        expect(first.compare(second)).toEqual(-1);
        expect(second.compare(first)).toEqual(1);
    });

    it('should be equal for non UCH hospitals', function() {
        var datacopy = angular.copy(episodeData);
        datacopy.location[0].hospital = 'RFH';
        var first       = new Episode(datacopy);
        var second      = new Episode(datacopy);
        expect(first.compare(second)).toEqual(0);
    });

    it('should allow custom comparators to be passed.', function() {
        var comparators = [jasmine.createSpy().and.returnValue(-1000)];
        var first       = new Episode(episodeData);
        var second      = new Episode(episodeData);
        expect(first.compare(second, comparators)).toEqual(0);
        expect(comparators[0]).toHaveBeenCalledWith(first)
        expect(comparators[0]).toHaveBeenCalledWith(second)
    });

    it('Should have access to the attributes', function () {
        expect(episode.active).toEqual(true);
    });

    it('Should convert date attributes to Date objects', function () {
        expect(episode.date_of_admission).toEqual(new Date(2013, 10, 19));
    });

    it('should create Items', function() {
        expect(episode.demographics.length).toBe(1);
        expect(episode.diagnosis.length).toBe(2);
    });

    it('should have access to attributes of items', function() {
        expect(episode.id).toBe(123);
        expect(episode.demographics[0].first_name).toBe('John');
        expect(episode.demographics[0].surname).toBe('Smith');
    });

    it('should be able to get specific item', function() {
        expect(episode.getItem('diagnosis', 1).id).toEqual(102);
    });

    it('should return the name of the patient', function() {
        expect(episode.getFullName()).toEqual('John Smith');
    });

    it('should know how many items it has in each column', function() {
        expect(episode.getNumberOfItems('demographics')).toBe(1);
        expect(episode.getNumberOfItems('diagnosis')).toBe(2);
    });

    it('getTags() should get the current tags', function(){
        expect(episode.getTags()).toEqual(['mine', 'tropical']);
    });

    it('should return tags if tagging is an Item()', function() {
        episode.tagging = [{makeCopy: function(){ return {
            mine: true,
            tropical: true,
            id: 1,
            _client: {something: 'else'}
        }; }}];
        expect(episode.getTags()).toEqual(['mine', 'tropical']);
    });

    it('should filter out _client from tags', function() {
        episode.tagging = [{makeCopy: function(){ return {
            mine: true,
            tropical: true,
            id: 1,
            _client: {something: 'else'}
        }; }}];
        expect(episode.getTags().indexOf('_client')).toEqual(-1);
    });

    it('hasTags() Should know if the episode has a given tag', function () {
        expect(episode.hasTag('tropical')).toEqual(true);
    });

    it('newItem() should create an Item', function() {
        var dd = new moment();
        var item = episode.newItem('diagnosis', {
          columnName: 'diagnosis'
        });
        expect(item.columnName).toBe('diagnosis');
    });

    it('should be able to add a new item', function() {
        var item = new Item(
            {id: 104, condition: 'Ebola', provisional: false,
             date_of_diagnosis: '19/02/2005'},
            episode,
            columns.fields.diagnosis
        );
        expect(episode.getNumberOfItems('diagnosis')).toBe(2);
        episode.addItem(item);
        expect(episode.getNumberOfItems('diagnosis')).toBe(3);
    });

    it('should addItems() for items without an entry on episode', function() {
        var item = {columnName: 'notareal_column'};
        episode.addItem(item);
        expect(episode.notareal_column).toEqual([item]);
    });

    it('removeItem() should remove an item from our episode', function() {
        // Note: Diagnoses end up ordered differently to the declared order
        // above as they are sorted by date.
        expect(episode.diagnosis.length).toEqual(2);
        episode.removeItem(episode.diagnosis[1]);
        expect(episode.diagnosis.length).toEqual(1);
        expect(episode.diagnosis[0].id).toBe(103);
    });

    it('Should be able to produce a copy of attributes', function () {
        expect(episode.makeCopy()).toEqual({
            id: 123,
            date_of_admission: new Date(2013, 10, 19),
            date_of_episode: new Date(2013, 10, 20),
            discharge_date: new Date(2016, 4, 25),
            category_name: 'inpatient',
            consistency_token: undefined
        });
    });

    describe('communicating with server', function (){
        var $httpBackend, episode;

        beforeEach(function(){
            inject(function($injector){
                $httpBackend = $injector.get('$httpBackend');
            });
        });

        afterEach(function(){
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        });


        describe('saving an existing episode', function (){
            var attrsJsonDate;

            beforeEach(function(){
                attrsJsonDate = {
                    id               : 555,
                    active           : true,
                    date_of_admission: '20/11/2013',
                    discharge_date   : null,
                    demographics: [{
                        id: 101,
                        patient_id: 99,
                        first_name: 'John',
                        surname: "Smith",
                        date_of_birth: '31/07/1980',
                        hospital_number: '555'
                    }]
                };

                episode = new Episode(episodeData);

                $httpBackend.whenPUT('/api/v0.1/episode/555/')
                    .respond(attrsJsonDate);

            });

            it('Should hit server', function () {
                $httpBackend.expectPUT('/api/v0.1/episode/555/', attrsJsonDate);
                episode.save(attrsJsonDate);
                $httpBackend.flush();
            });

            it('Should update item attributes', function () {
                $httpBackend.expectPUT('/api/v0.1/episode/555/', attrsJsonDate);
                episode.save(attrsJsonDate);
                $httpBackend.flush();
                expect(episode.date_of_admission).toEqual(new Date(2013, 10, 20))
            });

            it('Should translate dates to strings', function () {
                var toSave = angular.copy(attrsJsonDate);
                toSave.date_of_admission = new Date(2013, 10, 20);
                $httpBackend.expectPUT('/api/v0.1/episode/555/', attrsJsonDate);
                episode.save(toSave);
                $httpBackend.flush();
            });

            it('should cope with consistency token errors', function() {
                spyOn($window, 'alert');
                $httpBackend.expectPUT('/api/v0.1/episode/555/', attrsJsonDate)
                    .respond(409, {'error': 'Consistency tokens'});
                episode.save(attrsJsonDate);
                $httpBackend.flush();
                expect($window.alert).toHaveBeenCalled();
            });

            it('should cope with 500 errors', function() {
                spyOn($window, 'alert');
                $httpBackend.expectPUT('/api/v0.1/episode/555/', attrsJsonDate)
                    .respond(500, {'error': 'Cripes!'});
                episode.save(attrsJsonDate);
                $httpBackend.flush();
                expect($window.alert).toHaveBeenCalledWith('Item could not be saved');
            });

        });

        describe('isDischarged()', function() {

            it('should return true', function() {
                expect(episode.isDischarged()).toEqual(true);
            });

        });

        describe('findByHospitalNumber()', function (){
            it('Should call the newPatient callback', function () {
                var mock_new = jasmine.createSpy('Mock for new patient')
                var search_url = '/search/patient/';
                search_url += '?hospital_number=notarealnumber'
                $httpBackend.expectGET(search_url).respond([]);

                Episode.findByHospitalNumber('notarealnumber', {newPatient: mock_new})

                $httpBackend.flush();
                $scope.$digest(); // Fire actual resolving
                expect(mock_new).toHaveBeenCalled();
            });

            it('Should cast the new patient and call the newForPatient callback', function () {
                var mock_new = jasmine.createSpy('Mock for new patient')
                var search_url = '/search/patient/';
                search_url += '?hospital_number=notarealnumber'
                $httpBackend.expectGET(search_url).respond([episodeData]);
                Episode.findByHospitalNumber('notarealnumber', {newForPatient: mock_new})
                $httpBackend.flush();
                $scope.$digest(); // Fire actual resolving

                expect(mock_new).toHaveBeenCalled();
                var call_args = mock_new.calls.argsFor(0)[0]
                expect(call_args.demographics[0].date_of_birth.format('DD/MM/YY')).toEqual('31/07/80');
                expect(call_args.demographics[0].first_name).toEqual('John');
                expect(call_args.demographics[0].surname).toEqual('Smith');
            });


        });

    });
});
