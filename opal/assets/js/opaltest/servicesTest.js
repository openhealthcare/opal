describe('services', function() {
	var columns, patientData;

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
		patientData = {
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
			expect(schema.getColumn(1).name).toBe('diagnosis');
		});

		it('should be able to get the name of a column', function() {
			expect(schema.getColumnName(1)).toBe('diagnosis');
		});

		it('should know whether a column is a singleton', function() {
			expect(schema.isSingleton(0)).toBe(true);
			expect(schema.isSingleton(1)).toBe(false);
		});
	});

	describe('Options', function() {
		var Options, options;
		var data = {
			condition: {
				options: ['CAP', 'Community Acquired Pneumonia', 'Dengue'],
				synonyms: {'Community Acquired Pneumonia': 'CAP'}
			},
			destination: {
				options: ['Canada', 'Denmark'],
				synonyms: {}
			}
		};

		beforeEach(function() {
			inject(function($injector) {
				Options = $injector.get('Options');
				options = new Options(data);
			});
		});

		it('should find a synonym if it exists', function() {
			expect(options.getSynonymn('condition', 'Community Acquired Pneumonia')).toBe('CAP');
		});

		it('should return original term if no synonym exists', function() {
			expect(options.getSynonymn('condition', 'Dengue')).toBe('Dengue');
		});
	});

	describe('Patient', function() {
		var Patient, patient, PatientResource, resource, Schema, schema, Item;

		beforeEach(function() {
			inject(function($injector) {
				PatientResource = $injector.get('PatientResource');
				Patient = $injector.get('Patient');
				Schema = $injector.get('Schema');
				Item = $injector.get('Item');
			});

			schema = new Schema(columns);
			resource = new PatientResource(patientData);
			patient = new Patient(resource, schema);
		});

		it('should create Items', function() {
			expect(patient.demographics[0].constructor).toBe(Item);
			expect(patient.diagnosis[0].constructor).toBe(Item);
			expect(patient.diagnosis[1].constructor).toBe(Item);
		});

		it('should have access to attributes of items', function() {
			expect(patient.id).toBe(123);
			expect(patient.demographics[0].name).toBe('John Smith');
		});

		it('should be able to get specific item', function() {
			expect(patient.getItem(1, 1).id).toEqual(103);
		});

		it('should know how many items it has in each column', function() {
			expect(patient.getNumberOfItems(0)).toBe(1);
			expect(patient.getNumberOfItems(1)).toBe(2);
		});

		it('should be able to add a new item', function() {
			var item = new Item(
				{id: 104, condition: 'Ebola', provisional: false},
			       	patient,
			       	schema.getColumn(1)
			);
			patient.addItem(item);
			expect(patient.getNumberOfItems(1)).toBe(3);
			expect(patient.getItem(1, 2).id).toBe(104);
		});
	});

	describe('Item', function() {
		var Item, item;
		var mockPatient = {
			addItem: function(item) {},
			demographics: [{name: 'Name'}]
		};

		beforeEach(function() {
			inject(function($injector) {
				Item = $injector.get('Item');
			});

			item = new Item(patientData.demographics[0], mockPatient, columns[0]);
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
//				date_of_birth: new Date(1980, 6, 31)
			});
		});

		describe('communicating with server', function() {
			var $httpBackend;

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
				var attrs;

				beforeEach(function() {
					attrs = {id: 102, condition: 'Dengue', provisional: false};
					item = new Item(patientData.diagnosis[1], mockPatient, columns[1]);
					$httpBackend.whenPUT('/patient/diagnosis/102/').respond(attrs);
				});

				it('should hit server', function() {
					$httpBackend.expectPUT('/patient/diagnosis/102/');
					item.save(attrs);
					$httpBackend.flush();
				});

				it('should update item attributes', function() {
					item.save(attrs);
					$httpBackend.flush();
					expect(item.id).toBe(102);
					expect(item.condition).toBe('Dengue');
					expect(item.provisional).toBe(false);
				});
			});

			describe('saving new item', function() {
				var attrs;

				beforeEach(function() {
					attrs = {id: 104, condition: 'Ebola', provisional: false};
					item = new Item({}, mockPatient, columns[1]);
					$httpBackend.whenPOST('/patient/diagnosis/').respond(attrs);
				});

				it('should hit server', function() {
					$httpBackend.expectPOST('/patient/diagnosis/');
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

				it('should notify patient', function() {
					spyOn(mockPatient, 'addItem');
					item.save(attrs);
					$httpBackend.flush();
					expect(mockPatient.addItem).toHaveBeenCalled();
				});
			});
		});
	});

	describe('patientsLoader', function() {
		var patientsLoader, $httpBackend;

		beforeEach(function() {
			inject(function($injector) {
				patientsLoader = $injector.get('patientsLoader');
				$httpBackend = $injector.get('$httpBackend');
				$rootScope = $injector.get('$rootScope');
			});
		});

		it('should resolve to an array of patients', function() {
			var promise = patientsLoader();
			var patients;

			$httpBackend.whenGET('/schema/').respond(columns);
			$httpBackend.whenGET('/patient').respond([patientData]); // TODO trailing slash?
			promise.then(function(value) {
				patients = value;
			});

			$httpBackend.flush();
			$rootScope.$apply();

			expect(patients.length).toBe(1);
			expect(patients[0].id).toBe(123);
		});
	});

	describe('patientLoader', function() {
		var patientLoader, $httpBackend;

		beforeEach(function() {
			inject(function($injector) {
				patientLoader = $injector.get('patientLoader');
				$httpBackend = $injector.get('$httpBackend');
				$rootScope = $injector.get('$rootScope');
				$route = $injector.get('$route');
			});
		});

		xit('should resolve to a single patient', function() {
			// TODO unskip this
			// Skipping this, because I can't work out how to set $route.current
			// so that patientLoader can access it.
			var promise = patientLoader();
			var patient;

			$route.current = {params: {id: 123}};
			$httpBackend.whenGET('/schema/').respond(columns);
			$httpBackend.whenGET('/patient/123').respond(patientData); // TODO trailing slash?
			promise.then(function(value) {
				patient = value;
			});

			$httpBackend.flush();
			$rootScope.$apply();

			expect(patient.id).toBe(123);
		});
	});
});
