// TODO make this a service
var CATEGORIES = ['Inepisode', 'Review', 'Followup', 'Transferred', 'Discharged', 'Deceased'];

var services = angular.module('opal.services', ['ngResource']);

services.factory('EpisodeResource', function($resource) {
	return $resource('/records/episode/:id/', {id: '@id'})
});

services.factory('listSchemaLoader', function($q, $http, Schema) {
	var deferred = $q.defer();
	$http.get('/schema/list/').then(function(response) {
		var columns = response.data;
		deferred.resolve(new Schema(columns));
	}, function() {
		// handle error better
		alert('List schema could not be loaded');
	});

	return deferred.promise;
});

services.factory('detailSchemaLoader', function($q, $http, Schema) {
	var deferred = $q.defer();
	$http.get('/schema/detail/').then(function(response) {
		var columns = response.data;
		deferred.resolve(new Schema(columns));
	}, function() {
		// handle error better
		alert('Detail schema could not be loaded');
	});

	return deferred.promise;
});

services.factory('Schema', function() {
	return function(columns) {
		this.columns = columns;

		this.getNumberOfColumns = function() {
			return columns.length;
		};

		this.getColumn = function(columnName) {
			var column;
			for (cix = 0; cix < this.getNumberOfColumns(); cix++) {
				column = columns[cix];
				if (column.name == columnName) {
					return column;
				}
			}
			throw 'No such column with name: "' + columnName + '"';
		};

		this.isSingleton = function(columnName) {
			var column = this.getColumn(columnName);
			return column.single;
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

services.factory('episodesLoader', function($q, EpisodeResource, Episode, listSchemaLoader) {
	return function() {
		var deferred = $q.defer();
		listSchemaLoader.then(function(schema) {
			EpisodeResource.query(function(resources) {
				var episodes = {};
				_.each(resources, function(resource) {
					episodes[resource.id] = new Episode(resource, schema);
				});
				deferred.resolve(episodes);
			}, function() {
				// handle error better
				alert('Episodes could not be loaded');
			});
		});
		return deferred.promise;
	};
});

services.factory('episodeLoader', function($q, $route, EpisodeResource, Episode, detailSchemaLoader) {
	return function() {
		var deferred = $q.defer();
		detailSchemaLoader.then(function(schema) {
			EpisodeResource.get({id: $route.current.params.id}, function(resource) {
				var episode = new Episode(resource, schema);
				deferred.resolve(episode);
			}, function() {
				// handle error better
				alert('Episode could not be loaded');
			});
		});
		return deferred.promise;
	};
});

services.factory('Episode', function($http, $q, Item) {
	return function(resource, schema) {
		var episode = this;
	   	var column, field, attrs;

		angular.extend(episode, resource);

		for (var cix = 0; cix < schema.getNumberOfColumns(); cix++) {
			column = schema.columns[cix];
			for (var iix = 0; iix < episode[column.name].length; iix++) {
				attrs = episode[column.name][iix];
				episode[column.name][iix] = new Item(attrs, episode, column);
			};
		};

		this.getNumberOfItems = function(columnName) {
			return episode[columnName].length;
		};

		this.newItem = function(columnName) {
			var attrs = {};
			// TODO don't hardcode this
			if (columnName == 'microbiology_test') {
				attrs.date_ordered = moment().format('YYYY-MM-DD');
			}
			if (columnName == 'general_note') {
				attrs.date = moment().format('YYYY-MM-DD');
			}
			if (columnName == 'antimicrobial') {
				attrs.start_date = moment().format('YYYY-MM-DD');
			}
			if (columnName == 'diagnosis') {
				attrs.date_of_diagnosis = moment().format('YYYY-MM-DD');
			}
			return new Item(attrs, episode, schema.getColumn(columnName));
		};

		this.getItem = function(columnName, iix) {
			return episode[columnName][iix];
		};

		this.addItem = function(item) {
			episode[item.columnName].push(item);
		};

		this.removeItem = function(item) {
			var items = episode[item.columnName];
			for (iix = 0; iix < items.length; iix++) {
				if (item.id == items[iix].id) {
					items.splice(iix, 1);
					break;
				};
			};
		};

		this.isVisible = function(tag, subtag, hospital, ward) {
			var location = episode.location[0];
			if (location.tags[tag] != true) {
				return false;
			}
			if (subtag != 'all' && location.tags[subtag] != true){
				return false;
			}
			if (location.hospital.toLowerCase().indexOf(hospital.toLowerCase()) == -1) {
				return false;
			}
			if (location.ward.toLowerCase().indexOf(ward.toLowerCase()) == -1) {
				return false;
			}
			return true;
		};

		this.compare = function(other) {
			var v1, v2;
			var comparators = [
				function(p) { return CATEGORIES.indexOf(p.location[0].category) },
				function(p) { return p.location[0].hospital },
				function(p) {
					if (p.location[0].hospital == 'UCH' && p.location[0].ward.match(/^T\d+/)) {
						return parseInt(p.location[0].ward.substring(1));
					} else {
						return p.location[0].ward
					}
				},
				function(p) { return parseInt(p.location[0].bed) }
			];

			for (var ix = 0; ix < comparators.length; ix++) {
				v1 = comparators[ix](episode);
				v2 = comparators[ix](other);
				if (v1 < v2) {
					return -1;
				} else if (v1 > v2) {
					return 1;
				}
			}

			return 0;
		};
	};
});

services.factory('Item', function($http, $q) {
	return function(attrs, episode, columnSchema) {
		var item = this;

		this.initialise = function(attrs) {
			// Copy all attributes to item, and change any date fields to Date objects
			var field, value;

			angular.extend(item, attrs);
			for (var fix = 0; fix < columnSchema.fields.length; fix++) {
				field = columnSchema.fields[fix];
				value = item[field.name];
				if (field.type == 'date' && item[field.name]) {
					// Convert values of date fields to Date objects
					item[field.name] = moment(item[field.name], 'YYYY-MM-DD')._d;
				};
			};
		};

		this.columnName = columnSchema.name;

		this.episodeName = episode.demographics[0].name;

		this.makeCopy = function() {
			var field, value;
			var copy = {id: item.id};

			for (var fix = 0; fix < columnSchema.fields.length; fix++) {
				field = columnSchema.fields[fix];
				value = item[field.name];
				if (field.type == 'date' && item[field.name]) {
					// Convert values of date fields to strings of format DD/MM/YYYY
					copy[field.name] = moment(value).format('DD/MM/YYYY');
				} else {
					copy[field.name] = _.clone(value);
				};
			};

			return copy;
		};

		this.save = function(attrs) {
			var field, value;
			var deferred = $q.defer();
			var url = '/records/' + this.columnName + '/';
			var method;

			for (var fix = 0; fix < columnSchema.fields.length; fix++) {
				field = columnSchema.fields[fix];
				value = attrs[field.name];
				if (field.type == 'date' && attrs[field.name]) {
					// Convert values of date fields to strings of format YYYY-MM-DD
					if (angular.isString(value)) {
						value = moment(value, 'DD/MM/YYYY');
					} else {
						value = moment(value);
					};
					attrs[field.name] = value.format('YYYY-MM-DD');
				};
			};

			if (angular.isDefined(item.id)) {
				method = 'put';
				url += attrs.id + '/';
			} else {
				method = 'post';
				attrs['episode_id'] = episode.id;
			}

			$http[method](url, attrs).then(function(response) {
				item.initialise(response.data);
				if (method == 'post') {
					episode.addItem(item);
				};
				deferred.resolve();
			}, function(response) {
				// handle error better
				if (response.status == 409) {
					alert('Item could not be saved because somebody else has recently changed it - refresh the page and try again');
				} else {
					alert('Item could not be saved');
				};
			});
			return deferred.promise;
		};

		this.destroy = function() {
			var deferred = $q.defer();
			var url = '/records/' + item.columnName + '/' + item.id + '/';

			$http['delete'](url).then(function(response) {
				episode.removeItem(item);
				deferred.resolve();
			}, function(response) {
				// handle error better
				alert('Item could not be deleted');
			});
			return deferred.promise;
		};

		this.initialise(attrs);
	};
});
