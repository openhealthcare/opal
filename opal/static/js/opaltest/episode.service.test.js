describe('Episode', function() {
    var Episode, EpisodeResource, Item, $scope;
    var episode, episodeData, resource, tag_hierarchy;
    var $routeParams;

    beforeEach(function() {
        module('opal.services');

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

        episodeData = {
            id: 123,
            date_of_admission: "2013-11-19",
            category: 'inpatient',
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

        inject(function($injector) {
            Episode = $injector.get('Episode');
            Item = $injector.get('Item');
            $rootScope  = $injector.get('$rootScope');
            $scope      = $rootScope.$new();
            $routeParams = $injector.get('$routeParams');
        });

        episode = new Episode(episodeData);
    });

    it('should run walkin comparison in walkin review', function(){
        $routeParams.tag = "walkin";
        $routeParams.subtag = "walkin_review";
        var johnSmith = new Episode(episodeData);
        var anneAngelaData = angular.copy(episodeData);
        anneAngelaData.demographics[0].name = "Anne Angela";
        var anneAngela = new Episode(anneAngelaData);
        expect(johnSmith.compare(anneAngela)).toEqual(1);

        johnSmith.date_of_episode = new Date(2015, 10, 11);
        johnSmithOld = new Episode(episodeData);
        johnSmithOld.date_of_episode = new Date(2015, 10, 10);
        expect(johnSmithOld.compare(johnSmith)).toEqual(-1);

        anneAngela.date_of_episode = new Date(2015, 10, 12);
        expect(johnSmith.compare(anneAngela)).toEqual(-1);
    });

    it('Should have access to the attributes', function () {
        expect(episode.active).toEqual(true);
    });

    it('Should convert date attributes to Date objects', function () {
        expect(episode.date_of_admission).toEqual(new Date(2013, 10, 19))
    });

    it('should create Items', function() {
        expect(episode.demographics.length).toBe(1);
        expect(episode.diagnosis.length).toBe(2);
    });

    it('should have access to attributes of items', function() {
        expect(episode.id).toBe(123);
        expect(episode.demographics[0].name).toBe('John Smith');
    });

    it('should be able to get specific item', function() {
        expect(episode.getItem('diagnosis', 1).id).toEqual(103);
    });

    it('should know how many items it has in each column', function() {
        expect(episode.getNumberOfItems('demographics')).toBe(1);
        expect(episode.getNumberOfItems('diagnosis')).toBe(2);
    });

    it('getTags() should get the current tags', function(){
        expect(episode.getTags()).toEqual(['mine', 'tropical'])
    });

    it('hasTags() Should know if the episode has a given tag', function () {
        expect(episode.hasTag('tropical')).toEqual(true);
    });

    describe('childTags()', function (){

        it('Should return child tags', function () {
            expect(episode.childTags(tag_hierarchy)).toEqual(['mine', 'tropical'])
        });

        it('Should exclude parent tags', function () {
            episode.tagging[0].micro = true;
            episode.tagging[0].haem = true;
            var children = ['mine', 'tropical', 'haem'];
            expect(episode.childTags(tag_hierarchy)).toEqual(children);
        });

    });

    it('should be able to add a new item', function() {
        var item = new Item(
            {id: 104, condition: 'Ebola', provisional: false,
             date_of_diagnosis: '2005-02-18'},
            episode,
            columns.fields.diagnosis
        );
        expect(episode.getNumberOfItems('diagnosis')).toBe(2);
        episode.addItem(item);
        expect(episode.getNumberOfItems('diagnosis')).toBe(3);
    });

    it('Should be able to produce a copy of attributes', function () {
        expect(episode.makeCopy()).toEqual({
            id: 123,
            date_of_admission: new Date(2013, 10, 19),
            date_of_episode: null,
            discharge_date: null,
            category: 'inpatient',
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
            var attrsJsonDate, attrsHumanDate;

            beforeEach(function(){
                attrsJsonDate = {
                    id               : 555,
                    active           : true,
                    date_of_admission: '2013-11-20',
                    discharge_date   : null
                };
                attrsHumanDate = {
                    id               : 555,
                    active           : true,
                    date_of_admission: '20/11/2013',
                    discharge_date   : null
                }

                episode = new Episode(episodeData);

                $httpBackend.whenPUT('/episode/555/')
                    .respond(attrsJsonDate);

            });

            it('Should hit server', function () {
                $httpBackend.expectPUT('/episode/555/', attrsJsonDate);
                episode.save(attrsHumanDate);
                $httpBackend.flush();
            });

            it('Should update item attributes', function () {
                $httpBackend.expectPUT('/episode/555/', attrsJsonDate);
                episode.save(attrsHumanDate);
                $httpBackend.flush();
                expect(episode.date_of_admission).toEqual(new Date(2013, 10, 20))
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

            it('Should call the newForPatient callback', function () {
                var mock_new = jasmine.createSpy('Mock for new patient')
                var search_url = '/search/patient/';
                search_url += '?hospital_number=notarealnumber'
                $httpBackend.expectGET(search_url).respond([episodeData]);

                Episode.findByHospitalNumber('notarealnumber', {newForPatient: mock_new})

                $httpBackend.flush();
                $scope.$digest(); // Fire actual resolving

                expect(mock_new).toHaveBeenCalled();
            });


        });

    });
});
