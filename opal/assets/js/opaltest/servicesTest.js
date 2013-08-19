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
			expect(schema.getColumn('diagnosis').name).toBe('diagnosis');
		});

		it('should know whether a column is a singleton', function() {
			expect(schema.isSingleton('demographics')).toBe(true);
			expect(schema.isSingleton('diagnosis')).toBe(false);
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
			expect(patient.getItem('diagnosis', 1).id).toEqual(103);
		});

		it('should know how many items it has in each column', function() {
			expect(patient.getNumberOfItems('demographics')).toBe(1);
			expect(patient.getNumberOfItems('diagnosis')).toBe(2);
		});

		it('should be able to add a new item', function() {
			var item = new Item(
				{id: 104, condition: 'Ebola', provisional: false},
			       	patient,
			       	schema.getColumn('diagnosis')
			);
			patient.addItem(item);
			expect(patient.getNumberOfItems('diagnosis')).toBe(3);
			expect(patient.getItem('diagnosis', 2).id).toBe(104);
		});

		it('should be able to remove an item', function() {
			var item = patient.getItem('diagnosis', 0);
			patient.removeItem(item);
			expect(patient.getNumberOfItems('diagnosis')).toBe(1);
			expect(patient.getItem('diagnosis', 0).id).toBe(103);
		});
	});

	describe('Item', function() {
		var Item, item;
		var mockPatient = {
			addItem: function(item) {},
			removeItem: function(item) {},
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
					item = new Item(patientData.demographics[0], mockPatient, columns[0]);
					$httpBackend.whenPUT('/patient/demographics/101/').respond(attrsWithJsonDate);
				});

				it('should hit server', function() {
					$httpBackend.expectPUT('/patient/demographics/101/', attrsWithJsonDate);
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

			describe('deleting item', function() {
				beforeEach(function() {
					item = new Item(patientData.diagnosis[1], mockPatient, columns[1]);
					$httpBackend.whenDELETE('/patient/diagnosis/103/').respond();
				});

				it('should hit server', function() {
					$httpBackend.expectDELETE('/patient/diagnosis/103/');
					item.destroy();
					$httpBackend.flush();
				});

				it('should notify patient', function() {
					spyOn(mockPatient, 'removeItem');
					item.destroy();
					$httpBackend.flush();
					expect(mockPatient.removeItem).toHaveBeenCalled();
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

			$httpBackend.whenGET('/schema/list/').respond(columns);
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
