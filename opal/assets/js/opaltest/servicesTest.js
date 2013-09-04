describe('services', function() {
	var columns, episodeData;

	beforeEach(function() {
		module('opal.services');
		columns = [
			{
				name: 'demographics',
			   	single: true,
			   	fields: [
					{name: 'name', type: 'string'},
					{name: 'date_of_birth', type: 'date'},
				]},
			{
				name: 'diagnosis',
				single: false,
				fields: [
					{name: 'condition', type: 'string'},
					{name: 'provisional', type: 'boolean'},
				]},
		];
		episodeData = {
			id: 123,
			demographics: [{
				id: 101,
				name: 'John Smith',
				date_of_birth: '1980-07-31'
			}],
			diagnosis: [{
				id: 102,
				condition: 'Dengue',
				provisional: true,
			}, {
				id: 103,
				condition: 'Malaria',
				provisional: false,
			}]
		}
	});

	describe('Schema', function() {
		var Schema, schema;

		beforeEach(function() {
			inject(function($injector) {
				Schema = $injector.get('Schema');
			});
			schema = new Schema(columns);
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

	describe('Episode', function() {
		var Episode, episode, EpisodeResource, resource, Schema, schema, Item;

		beforeEach(function() {
			inject(function($injector) {
				EpisodeResource = $injector.get('EpisodeResource');
				Episode = $injector.get('Episode');
				Schema = $injector.get('Schema');
				Item = $injector.get('Item');
			});

			schema = new Schema(columns);
			resource = new EpisodeResource(episodeData);
			episode = new Episode(resource, schema);
		});

		it('should create Items', function() {
			expect(episode.demographics[0].constructor).toBe(Item);
			expect(episode.diagnosis[0].constructor).toBe(Item);
			expect(episode.diagnosis[1].constructor).toBe(Item);
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

		it('should be able to add a new item', function() {
			var item = new Item(
				{id: 104, condition: 'Ebola', provisional: false},
			       	episode,
			       	schema.getColumn('diagnosis')
			);
			episode.addItem(item);
			expect(episode.getNumberOfItems('diagnosis')).toBe(3);
			expect(episode.getItem('diagnosis', 2).id).toBe(104);
		});

		it('should be able to remove an item', function() {
			var item = episode.getItem('diagnosis', 0);
			episode.removeItem(item);
			expect(episode.getNumberOfItems('diagnosis')).toBe(1);
			expect(episode.getItem('diagnosis', 0).id).toBe(103);
		});
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

			item = new Item(episodeData.demographics[0], mockEpisode, columns[0]);
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
					item = new Item(episodeData.demographics[0], mockEpisode, columns[0]);
					$httpBackend.whenPUT('/records/demographics/101/').respond(attrsWithJsonDate);
				});

				it('should hit server', function() {
					$httpBackend.expectPUT('/records/demographics/101/', attrsWithJsonDate);
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
					item = new Item({}, mockEpisode, columns[1]);
					$httpBackend.whenPOST('/records/diagnosis/').respond(attrs);
				});

				it('should hit server', function() {
					$httpBackend.expectPOST('/records/diagnosis/');
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
					item = new Item(episodeData.diagnosis[1], mockEpisode, columns[1]);
					$httpBackend.whenDELETE('/records/diagnosis/103/').respond();
				});

				it('should hit server', function() {
					$httpBackend.expectDELETE('/records/diagnosis/103/');
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
				episodesLoader = $injector.get('episodesLoader');
				$httpBackend = $injector.get('$httpBackend');
				$rootScope = $injector.get('$rootScope');
			});
		});

		it('should resolve to an object of episodes', function() {
			var promise = episodesLoader();
			var episodes;

			$httpBackend.whenGET('/schema/list/').respond(columns);
			$httpBackend.whenGET('/records/episode').respond([episodeData]); // TODO trailing slash?
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
			$httpBackend.whenGET('/records/episode/123').respond(episodeData); // TODO trailing slash?
			promise.then(function(value) {
				episode = value;
			});

			$httpBackend.flush();
			$rootScope.$apply();

			expect(episode.id).toBe(123);
		});
	});
});
