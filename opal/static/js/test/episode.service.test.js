describe('Episode', function() {
    "use strict";

    var Episode, EpisodeResource, Item, $scope, $rootScope, columns, $window;
    var episode, episodeData, resource, tag_hierarchy, fields;
    var $routeParams, opalTestHelper;

    beforeEach(function() {
        module('opal.services');
        module('opal.test');

        inject(function($injector) {
            Episode = $injector.get('Episode');
            Item = $injector.get('Item');
            $rootScope  = $injector.get('$rootScope');
            $scope      = $rootScope.$new();
            $routeParams = $injector.get('$routeParams');
            $window      = $injector.get('$window');
            opalTestHelper = $injector.get('opalTestHelper');
        });
        episode = opalTestHelper.newEpisode($rootScope);
        episodeData = opalTestHelper.getEpisodeData();
    });

    describe('initialisation', function() {

        it('should throw if there is no patient ID', function() {
            expect(function(){ new Episode({});}).toThrow();
        });

        it('should cast dates on the episode if appropriate', function(){
            var newEpisode = new Episode(episodeData);
            expect(moment(newEpisode.start).format('DD/MM/YYYY')).toEqual("19/11/2013");
            expect(moment(newEpisode.end).format('DD/MM/YYYY')).toEqual("25/05/2016");
        });
    });

    describe('compare', function(){
      it('should allow custom comparators to be passed.', function() {
          var comparators = [jasmine.createSpy().and.returnValue(-1000)];
          var first       = new Episode(episodeData);
          var second      = new Episode(episodeData);
          expect(first.compare(second, comparators)).toEqual(0);
          expect(comparators[0]).toHaveBeenCalledWith(first)
          expect(comparators[0]).toHaveBeenCalledWith(second)
      });

      it('should compare on start equal', function(){
        var first = new Episode(episodeData);
        var second = new Episode(episodeData);
        expect(first.compare(second)).toEqual(0);
      });

      it('should compare on start positive', function(){
        var first = new Episode(episodeData);
        first.start = moment(new Date(2017, 11, 1));
        var second = new Episode(episodeData);
        second.start = moment(new Date(2017, 12, 1));
        expect(first.compare(second)).toEqual(1);
      });

      it('should compare on start negative', function(){
        var first = new Episode(episodeData);
        first.start = moment(new Date(2017, 11, 1));
        var second = new Episode(episodeData);
        second.start = moment(new Date(2017, 10, 1));
        expect(first.compare(second)).toEqual(-1);
      });

      it('should compare on first_name equal', function(){
        var first = new Episode(episodeData);
        first.first_name = "Jane"
        var second = new Episode(episodeData);
        second.first_name = "Jane"
        expect(first.compare(second)).toEqual(0);
      });

      it('should compare on first_name negative', function(){
        var first = new Episode(episodeData);
        first.first_name = "Jane"
        var second = new Episode(episodeData);
        second.first_name = "Steve"
        expect(first.compare(second)).toEqual(-1);
      });

      it('should compare on first_name positive', function(){
        var first = new Episode(episodeData);
        first.first_name = "Steve"
        var second = new Episode(episodeData);
        second.first_name = "Jane"
        expect(first.compare(second)).toEqual(1);
      });

      it('should compare on surname equal', function(){
        var first = new Episode(episodeData);
        first.sirname = "Marlowe"
        var second = new Episode(episodeData);
        second.sirname = "Marlowe"
        expect(first.compare(second)).toEqual(0);
      });

      it('should compare on surname positive', function(){
        var first = new Episode(episodeData);
        first.surname = "Shakespeare"
        var second = new Episode(episodeData);
        second.surname = "Marlowe"
        expect(first.compare(second)).toEqual(1);
      });

      it('should compare on surname negative', function(){
        var first = new Episode(episodeData);
        first.surname = "Marlowe"
        var second = new Episode(episodeData);
        second.surname = "Shakespeare"
        expect(first.compare(second)).toEqual(-1);
      });
    });

    it('Should have access to the attributes', function () {
        expect(episode.active).toEqual(true);
    });

    it('Should convert date attributes to moment objects', function () {
        expect(episode.start.toDate()).toEqual(new Date(2013, 10, 19));
    });

    it('Should raise an error if they try to get discharge date', function(){
        var shouldThrow = function(){episode.discharge_date; };
        expect(shouldThrow).toThrow(
          "Discharge date is deprecated in opal 0.9.0, use end"
        );
    });

    it('Should raise an error if they try to set discharge date', function(){
      var shouldThrow = function(){episode.discharge_date = "as";}
      expect(shouldThrow).toThrow(
        "Discharge date is deprecated in opal 0.9.0, use end"
      );
    });

    it('Should raise an error if they try to set date of admission', function(){
      var shouldThrow = function(){episode.date_of_admission = "as";}
      expect(shouldThrow).toThrow(
        "Date of admission is deprecated in opal 0.9.0, use start"
      );
    });

    it('Should raise an error if they try to get date of admission', function(){
      var shouldThrow = function(){episode.date_of_admission; };
      expect(shouldThrow).toThrow(
        "Date of admission is deprecated in opal 0.9.0, use start"
      );
    });

    it('Should raise an error if they try to get date of episode', function(){
      var shouldThrow = function(){episode.date_of_episode = "as";}
      expect(shouldThrow).toThrow(
        "Date of episode is deprecated in opal 0.9.0, use start"
      );
    });

    it('Should raise an error if they try to set date of episode', function(){
      var shouldThrow = function(){episode.date_of_episode; };
      expect(shouldThrow).toThrow(
        "Date of episode is deprecated in opal 0.9.0, use start"
      );
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
            opalTestHelper.getRecordLoaderData().diagnosis
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

    it('should sort items by their "sort" field if available' , function(){
        expect(episode.diagnosis[0].id).toBe(103);
        expect(episode.diagnosis[1].id).toBe(102);
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
        var copy = episode.makeCopy();
        expect(copy.id).toBe(123);
        expect(copy.category_name).toBe('Inpatient');
        expect(copy.consistency_token).toBe(undefined);
        expect(copy.start).toEqual(new Date(2013, 10, 19));
        expect(copy.end).toEqual(new Date(2016, 4, 25));
    });

    it('start and end should be null if not set', function(){
      var copy = episode.makeCopy();
      delete copy.start;
      delete copy.end;
      expect(copy.id).toBe(123);
      expect(copy.category_name).toBe('Inpatient');
      expect(copy.consistency_token).toBe(undefined);
      expect(copy.start).toEqual(undefined);
      expect(copy.end).toEqual(undefined);
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
                    start: '20/11/2013',
                    end: null,
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
                expect(episode.start.toDate()).toEqual(new Date(2013, 10, 20));
            });

            it('Should translate dates to strings', function () {
                var toSave = angular.copy(attrsJsonDate);
                toSave.start = new Date(2013, 10, 20);
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

            it('Should call the error callback on error', function () {
                var mock_new = jasmine.createSpy('Mock for new patient')
                var search_url = '/search/patient/';
                search_url += '?hospital_number=notarealnumber'
                $httpBackend.expectGET(search_url).respond([1, 2, 3]);
                var err = jasmine.createSpy();

                Episode.findByHospitalNumber('notarealnumber', {
                  newPatient: mock_new,
                  error: err
                })

                $httpBackend.flush();
                $scope.$digest();
                expect(err).toHaveBeenCalled();
            });

            it('should handle the case where no number is passed in', function(){
              var mock_new = jasmine.createSpy('Mock for new patient');

              Episode.findByHospitalNumber(null, {
                newPatient: mock_new
              });

              $scope.$digest();

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
