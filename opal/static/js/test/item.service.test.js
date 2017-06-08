describe('Item', function() {
    "use strict";

    var columns, episodeData, options, records, list_schema, mockWindow, $rootScope;

    beforeEach(function() {
        module('opal.services', function($provide){
            $provide.service('Demographics', function(){
                return function(x){ return x };
            });
        });

        columns = {
            "fields": {
                'demographics': {
                    name: "demographics",
                    single: true,
                    fields: [
                        {name: 'name', type: 'string'},
                        {name: 'date_of_birth', type: 'date'},
                        {name: 'created', type: 'date_time'},
                    ],
                    angular_service: 'Demographics'
                },
                "diagnosis": {
                    name: "diagnosis",
                    single: false,
                    sort: 'date_of_diagnosis',
                    fields: [
                        {name: 'date_of_diagnosis', type: 'date'},
                        {name: 'condition', type: 'string', default: 'flu'},
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
                date_of_birth: '31/07/1980',
                hospital_number: '555',
                created: "07/04/2015 11:45:00"
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
                date_of_diagnosis: '20/04/2007',
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
        };
    });

    describe('Item', function() {
        var Item, item;
        var mockEpisode = {
            addItem: function(item) {},
            removeItem: function(item) {},
            demographics: [{name: 'Name'}]
        };

        beforeEach(function() {
            mockWindow = { alert: jasmine.createSpy() };

            module(function($provide) {
                $provide.value('$window', mockWindow);
            });

            inject(function($injector) {
                Item = $injector.get('Item');
                $rootScope = $injector.get('$rootScope');
            });

            $rootScope.fields = columns.fields;
            item = new Item(episodeData.demographics[0], mockEpisode, columns.fields.demographics);
        });

        it('should have correct attributes', function() {
            expect(item.id).toBe(101)
            expect(item.name).toBe('John Smith');
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
          delete copy._client;
          expect(copy).toEqual({
              id: 101,
              name: 'John Smith',
              date_of_birth: new Date(1980, 6, 31),
              created: new Date(2015, 3, 7, 11, 45)
          });
        });

        it('should make a copy with defaults', function(){
            var newItem = new Item({}, mockEpisode, columns.fields.diagnosis);
            expect(!!newItem.condition).toBe(false);
            var copy = newItem.makeCopy();
            expect(copy.condition).toBe('flu');
        });

        it('defaults should not overwrite existing data', function(){
          var existing = new Item(episodeData.diagnosis[0], mockEpisode, columns.fields.diagnosis);
          expect(existing.condition).toBe('Dengue');
          var copy = existing.makeCopy();
          expect(copy.condition).toBe('Dengue');
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
                var attrsWithJsonDate;

                beforeEach(function() {
                    attrsWithJsonDate = {
                        id: 101,
                        name: 'John Smythe',
                        date_of_birth: '30/07/1980'
                    };
                    item = new Item(episodeData.demographics[0],
                                    mockEpisode,
                                    columns.fields.demographics);
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

            });

            describe('Failing save() calls', function() {
                var $httpBackend, item, editing;

                beforeEach(function() {
                    inject(function($injector) {
                        $httpBackend = $injector.get('$httpBackend');
                    });
                    item = new Item(
                        episodeData.demographics[0],
                        mockEpisode,
                        columns.fields.demographics
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
                    item = new Item(episodeData.diagnosis[1],
                                    mockEpisode, columns.fields.diagnosis);
                });

                it('should hit server', function() {
                    $httpBackend.whenDELETE('/api/v0.1/diagnosis/103/').respond();
                    $httpBackend.expectDELETE('/api/v0.1/diagnosis/103/');
                    item.destroy();
                    $httpBackend.flush();
                });

                it('should notify episode', function() {
                    $httpBackend.whenDELETE('/api/v0.1/diagnosis/103/').respond();
                    spyOn(mockEpisode, 'removeItem');
                    item.destroy();
                    $httpBackend.flush();
                    expect(mockEpisode.removeItem).toHaveBeenCalled();
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
});
