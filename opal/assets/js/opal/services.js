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

services.factory('Options', function() {
	return function(options) {
		this.options = options,
		this.getSynonymn = function(list, term) {
			return options[list].synonyms[term] || term;
		};
	};
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

services.factory('Patient', function($http, $q, utils) {
	return function(resource, schema) {
		var patient = this;
	   	var column, field, item;

		angular.extend(patient, resource);

		for (var cix = 0; cix < schema.getNumberOfColumns(); cix++) {
			column = schema.getColumn(cix);

			// Convert values of date fields to Date objects
			for (var fix = 0; fix < column.fields.length; fix++) {
				field = column.fields[fix];
				if (field.type == 'date') {
					for (var iix = 0; iix < patient[column.name].length; iix++) {
						item = patient[column.name][iix];
						item[field.name] = utils.parseDate(item[field.name]);
					};
				};
			};
		};

		this.getItem = function(cix, iix) {
			return patient[schema.getColumnName(cix)][iix];
		};

		this.copyItem = function(cix, iix) {
			return _.clone(this.getItem(cix, iix));
		};

		this.updateItem = function(cix, iix, attrs) {
			var deferred = $q.defer();
			var columnName = schema.getColumnName(cix);
			var url = '/patient/' + columnName + '/' + attrs.id + '/';

			$http.put(url, attrs).then(function(response) {
				patient[columnName][iix] = attrs;
				deferred.resolve();
			}, function(response) {
				// handle error better
				alert('Item could not be updated');
			});
			return deferred.promise;
		};

		this.addItem = function(cix, attrs) {
			var deferred = $q.defer();
			var columnName = schema.getColumnName(cix);
			var url = '/patient/' + columnName + '/';

			$http.post(url, attrs).then(function(response) {
				attrs.id = response.data.id;
				patient[columnName].push(attrs);
				deferred.resolve();
			}, function(response) {
				// handle error better
				alert('Item could not be added');
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
