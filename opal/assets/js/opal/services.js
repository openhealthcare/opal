var services = angular.module('opal.services', ['ngResource']);

services.factory('PatientResource', function($resource) {
	return $resource('/patient/:id/', {id: '@id'})
});

services.factory('schemaLoader', function($q, $http, Schema) {
	var deferred = $q.defer();
	$http.get('/schema/').then(function(response) {
		var columns = response.data;
		deferred.resolve(new Schema(columns));
	}, function() {
		// handle error better
		alert('Schema could not be loaded');
	});

	return deferred.promise;
});

services.factory('Schema', function() {
	return function(columns) {
		this.getNumberOfColumns = function() {
			return columns.length;
		};
		this.getColumn = function(cix) {
			return columns[cix];
		};
		this.getColumnName = function(cix) {
			return columns[cix].name;
		};
		this.isSingleton = function(cix) {
			return columns[cix].single;
		};
	};
});

services.factory('Options', function($q, $http) {
	var deferred = $q.defer();
	$http.get('/options/').then(function(response) {
		deferred.resolve(response.data);
	}, function() {
		// handle error better
		alert('Options could not be loaded');
	});

	return deferred.promise;
});

services.factory('patientsLoader', function($q, PatientResource, Patient, schemaLoader) {
	return function() {
		var deferred = $q.defer();
		schemaLoader.then(function(schema) {
			PatientResource.query(function(resources) {
				var patients = _.map(resources, function(resource) {
					return new Patient(resource, schema);
				});
				deferred.resolve(patients);
			}, function() {
				// handle error better
				alert('Patients could not be loaded');
			});
		});
		return deferred.promise;
	};
});

services.factory('patientLoader', function($q, $route, PatientResource, Patient, schemaLoader) {
	return function() {
		var deferred = $q.defer();
		schemaLoader.then(function(schema) {
			PatientResource.get({id: $route.current.params.id}, function(resource) {
				var patient = new Patient(resource, schema);
				deferred.resolve(patient);
			}, function() {
				// handle error better
				alert('Patient could not be loaded');
			});
		});
		return deferred.promise;
	};
});

services.factory('Patient', function($http, $q, Item, utils) {
	return function(resource, schema) {
		var patient = this;
	   	var column, field, attrs;

		angular.extend(patient, resource);

		for (var cix = 0; cix < schema.getNumberOfColumns(); cix++) {
			column = schema.getColumn(cix);

			for (var iix = 0; iix < patient[column.name].length; iix++) {
				attrs = patient[column.name][iix];
				patient[column.name][iix] = new Item(attrs, patient, column);
			};
		};

		this.getNumberOfItems = function(cix) {
			return patient[schema.getColumnName(cix)].length;
		};

		this.newItem = function(cix) {
			return new Item({}, patient, schema.getColumn(cix));
		};

		this.getItem = function(cix, iix) {
			return patient[schema.getColumnName(cix)][iix];
		};

		this.addItem = function(item) {
			patient[item.columnName].push(item);
		};
	};
});

services.factory('Item', function($http, $q, utils) {
	return function(attrs, patient, columnSchema) {
		var item = this;
		var field;

		angular.extend(item, attrs);

		// Convert values of date fields to Date objects
		for (var fix = 0; fix < columnSchema.fields.length; fix++) {
			field = columnSchema.fields[fix];
			if (field.type == 'date') {
				item[field.name] = utils.parseDate(item[field.name]);
			};
		};

		this.columnName = columnSchema.name;

		this.patientName = patient.demographics[0].name;

		this.makeCopy = function() {
			var field;
			var copy = {id: item.id};

			for (var fix = 0; fix < columnSchema.fields.length; fix++) {
				field = columnSchema.fields[fix];
				if (field.type != 'date') {
					// Currently cannot display date objects in form inputs
					// TODO fix this
					copy[field.name] = _.clone(item[field.name]);
				};
			};

			return copy;
		};

		this.save = function(attrs) {
			var deferred = $q.defer();
			var url = '/patient/' + this.columnName + '/';
			var method;

			if (angular.isDefined(item.id)) {
				method = 'put';
				url += attrs.id + '/';
			} else {
				method = 'post';
				attrs['patient_id'] = patient.id;
			}

			$http[method](url, attrs).then(function(response) {
				angular.extend(item, attrs);
				if (method == 'post') {
					patient.addItem(item);
				};
				deferred.resolve();
			}, function(response) {
				// handle error better
				alert('Item could not be saved');
			});
			return deferred.promise;
		};
	};
});

services.factory('utils', function() {
	return {
		parseDate: function(dateString) {
			if (angular.isString(dateString)) {
				var tokens = dateString.split('-');
				return new Date(tokens[0], tokens[1] - 1, tokens[2]);
			} else {
				return dateString;
			};
		}
	};
});
