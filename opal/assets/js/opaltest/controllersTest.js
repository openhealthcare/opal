describe('controllers', function() {
	var columns, patientData, Schema, schema, Patient;

	beforeEach(function() {
		module('opal.controllers');
		columns = [
			{
				name: 'demographics',
			   	single: true,
			   	fields: [
					{name: 'name', type: 'string'},
					{name: 'date_of_birth', type: 'date'},
				]},
			{
				name: 'location',
				single: true,
				fields: [
					{name: 'category', type: 'string'},
					{name: 'hospital', type: 'string'},
					{name: 'ward', type: 'string'},
					{name: 'bed', type: 'string'},
					{name: 'date_of_admission', type: 'date'},
					{name: 'tags', type: 'list'},
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
			location: [{
				category: 'Inpatient',
				hospital: 'UCH',
				ward: 'T10',
				bed: '15',
				date_of_admission: '2013-08-01',
				tags: ['mine', 'tropical']
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
		};

		inject(function($injector) {
			Schema = $injector.get('Schema');
			Patient = $injector.get('Patient');
		});

		schema = new Schema(columns);
	});

	describe('PatientListCtrl', function() {
		var $scope, $cookieStore, $controller, patients;

		beforeEach(function() {
			inject(function($injector) {
				$rootScope = $injector.get('$rootScope');
				$cookieStore = $injector.get('$cookieStore');
				$controller = $injector.get('$controller');
			});

			patients = [new Patient(patientData, schema)];
		});

		it('should be createable', function() {
			var controller = $controller('PatientListCtrl', {
				$scope: $rootScope.$new(),
				$cookieStore: $cookieStore,
				schema: schema,
				patients: patients
			});
		});
	});
});
