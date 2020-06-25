describe('Item', function() {
    "use strict";

    var episodeData, recordSchema, mockWindow;
    var opalTestHelper, $rootScope, Item, $httpBackend, item, episode;
    var angularServiceMock;

    beforeEach(function() {
        angularServiceMock = jasmine.createSpy();
        mockWindow = { alert: jasmine.createSpy() };
        module('opal.services', function($provide){
            $provide.service('Demographics', function(){
                return function(x){
                  angularServiceMock(x);
                  return x;
                };
            });
            $provide.value('$window', mockWindow);
        });
        module('opal.test');

        inject(function($injector) {
          opalTestHelper = $injector.get('opalTestHelper');
          Item = $injector.get('Item');
          $rootScope = $injector.get('$rootScope');
          $httpBackend = $injector.get('$httpBackend');
        });

        recordSchema = opalTestHelper.getRecordLoaderData();
        episodeData = opalTestHelper.getEpisodeData();
        episode = opalTestHelper.newEpisode($rootScope);
        spyOn(episode, "addItem");
        spyOn(episode, "removeItem");
        item = new Item(episodeData.demographics[0], episode, recordSchema.demographics);
    });

    it('should call a service function if one exists', function(){
      var demographicsWithService = angular.copy(recordSchema.demographics);
      demographicsWithService.angular_service = 'Demographics';
      new Item(episodeData.demographics[0], episode, demographicsWithService);
      expect(angularServiceMock).toHaveBeenCalled();
    });

    it('should have correct attributes', function() {
        expect(item.id).toBe(101)
        expect(item.first_name).toBe('John');
        expect(item.surname).toBe('Smith');
    });

    it('should convert values of date fields to moment objects', function() {
        expect(item.date_of_birth.toDate()).toEqual(new Date(1980, 6, 31));
    });

    it('should convert values of date time fields to moment objects', function() {
        expect(item.created.toDate()).toEqual(new Date(2015, 3, 7, 11, 45));
    });

    it('should supply a default formController of editItem', function() {
        expect(item.formController).toEqual('EditItemCtrl');
    });

    it('should be able to produce copy of attributes', function() {
      var copy = item.makeCopy();
      var id = copy._client.id;
      expect(id.indexOf('demographics')).toBe(0)
      var specificCopy = _.pick(copy, "id", "first_name", "surname", "date_of_birth", "created");
      expect(specificCopy).toEqual({
          id: 101,
          first_name: "John",
          surname: "Smith",
          date_of_birth: new Date(1980, 6, 31),
          created: new Date(2015, 3, 7, 11, 45)
      });
    });

    it('should make a copy with defaults', function(){
        var diagnosisSchema = angular.copy(recordSchema.diagnosis);
        var condition = _.findWhere(diagnosisSchema.fields, {name: "condition"});
        condition.default = 'flu';
        var newItem = new Item({}, episode, diagnosisSchema);
        expect(!!newItem.condition).toBe(false);
        var copy = newItem.makeCopy();
        expect(copy.condition).toBe('flu');
    });

    it('defaults should not overwrite existing data', function(){
      var existing = new Item(episodeData.diagnosis[0], episode, recordSchema.diagnosis);
      expect(existing.condition).toBe('Dengue');
      var copy = existing.makeCopy();
      expect(copy.condition).toBe('Dengue');
    });

    describe('communicating with server', function() {
        afterEach(function() {
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        });

        describe('saving existing item', function() {
            var attrsWithJsonDate;

            beforeEach(function() {
                attrsWithJsonDate = {
                    id: 101,
                    name: 'John Smythe',
                    date_of_birth: '30/07/1980'
                };
                item = new Item(episodeData.demographics[0],
                                episode,
                                recordSchema.demographics);
                $httpBackend.whenPUT('/api/v0.1/demographics/101/')
                    .respond(attrsWithJsonDate);
            });

            it('should hit server', function() {
                $httpBackend.expectPUT('/api/v0.1/demographics/101/', attrsWithJsonDate);
                item.save(attrsWithJsonDate);
                $httpBackend.flush();
            });

            it('should update item attributes', function() {
                item.save(attrsWithJsonDate);
                $httpBackend.flush();
                expect(item.id).toBe(101);
                expect(item.name).toBe('John Smythe');
                expect(item.date_of_birth.toDate()).toEqual(new Date(1980, 6, 30));
            });

          describe('tagging special casing', function() {

            it('should set the ids required', function() {
              var item = new Item(episodeData.tagging[0], episode, recordSchema.tagging);
              $httpBackend.expectPUT('/api/v0.1/tagging/123/', {'main': true, 'id': 123}).respond({});
              item.save({'main': true});
              $httpBackend.flush();
              expect(item.id).toBe(episode.id);
            });

          });

        });

        describe('Failing save() calls', function() {
            var $httpBackend, item, editing;

            beforeEach(function() {
                inject(function($injector) {
                    $httpBackend = $injector.get('$httpBackend');
                });
                item = new Item(
                    episodeData.demographics[0],
                    episode,
                    recordSchema.demographics
                );
                editing = {
                    id: 101,
                    name: 'John Smythe',
                    date_of_birth: '30/07/1980'
                };
            });

            afterEach(function() {
                $httpBackend.verifyNoOutstandingExpectation();
                $httpBackend.verifyNoOutstandingRequest();
            });

            it('should tell us if there was a conflict', function() {
                var msg = 'Item could not be saved because somebody else has \
recently changed it - refresh the page and try again';
                $httpBackend.whenPUT('/api/v0.1/demographics/101/').respond(409);
                item.save(editing);
                $httpBackend.flush();
                expect(mockWindow.alert).toHaveBeenCalledWith(msg);
            });

            it('should tell us if there is an error', function() {
                var msg = 'Item could not be saved';
                $httpBackend.whenPUT('/api/v0.1/demographics/101/').respond(500);
                item.save(editing);
                $httpBackend.flush();
                expect(mockWindow.alert).toHaveBeenCalledWith(msg);
            });

        });

        describe('saving new item', function() {
            var attrs;

            beforeEach(function() {
                attrs = {id: 104, condition: 'Ebola', provisional: false};
                item = new Item({}, episode, recordSchema.diagnosis);
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
                item.save(attrs);
                $httpBackend.flush();
                expect(episode.addItem).toHaveBeenCalled();
            });
        });

        describe('deleting item', function() {
            beforeEach(function() {
                item = new Item(episodeData.diagnosis[1],
                                episode, recordSchema.diagnosis);
            });

            it('should hit server', function() {
                $httpBackend.whenDELETE('/api/v0.1/diagnosis/103/').respond();
                $httpBackend.expectDELETE('/api/v0.1/diagnosis/103/');
                item.destroy();
                $httpBackend.flush();
            });

            it('should notify episode', function() {
                $httpBackend.whenDELETE('/api/v0.1/diagnosis/103/').respond();
                item.destroy();
                $httpBackend.flush();
                expect(episode.removeItem).toHaveBeenCalled();
            });

            it('should alert() when we fail a destroy call.', function() {
                $httpBackend.whenDELETE('/api/v0.1/diagnosis/103/').respond(500);
                item.destroy()
                $httpBackend.flush()
                expect(mockWindow.alert).toHaveBeenCalledWith('Item could not be deleted')
            });

        });
    });
});
