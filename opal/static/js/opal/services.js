// TODO make this a service
var CATEGORIES = [
    'Inepisode', 'Review', 'Followup', 'Transferred', 'Discharged', 'Deceased'
];

var services = angular.module('opal.services', ['ngResource']);

services.factory('EpisodeResource', function($resource, $q) {
    resource = $resource('/episode/:id/', {id: '@id'});
    return resource
});

services.factory('listSchemaLoader', function($q, $http, $window, $routeParams,
                                              Schema) {
    var deferred = $q.defer();
    $http.get('/schema/list/').then(function(response) {
	    var schemas = response.data;
        var schema = {default: new Schema(schemas.default)};

        _.each(_.reject(_.keys(schemas), function(k){ return k == 'default' }),
               function(key){
                   schema[key] = {default: new Schema(schemas[key].default)}
                   _.each(_.reject(_.keys(schemas), function(k){ return k == 'default' }),
                          function(subkey){
                              schema[key][subkey] = new Schema(schemas[key][subkey]);
                          });
        });

	    deferred.resolve(schema);
    }, function() {
	    // handle error better
	    $window.alert('List schema could not be loaded');
    });

    return deferred.promise;
});

services.factory('detailSchemaLoader', function($q, $http, $window, Schema) {
    var deferred = $q.defer();
    $http.get('/schema/detail/').then(function(response) {
        deferred.resolve(new Schema(response.data))
    }, function() {
	    // handle error better
	    $window.alert('Detail schema could not be loaded');
    });

    return deferred.promise;
});

services.factory('extractSchemaLoader', function($q, $http, $window, Schema){
    var deferred = $q.defer();
    $http.get('/schema/extract/').then(function(response) {
	    var columns = response.data;
	    deferred.resolve(new Schema(columns));
    }, function() {
	    // handle error better
	    $window.alert('Extract schema could not be loaded');
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

services.factory('Options', function($q, $http, $window) {
    var deferred = $q.defer();
    $http.get('/options/').then(function(response) {
	    deferred.resolve(response.data);
    }, function() {
	    // handle error better
	    $window.alert('Options could not be loaded');
    });
    return deferred.promise;
});

services.factory('episodesLoader', function($q, $window,
                                            EpisodeResource, Episode,
                                            listSchemaLoader) {
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
		        $window.alert('Episodes could not be loaded');
	        });
	    });
	    return deferred.promise;
    };
});


services.factory('dischargedEpisodesLoader', function($q, $window,
                                                      EpisodeResource, Episode,
                                                      listSchemaLoader) {
    return function() {
	    var deferred = $q.defer();
	    listSchemaLoader.then(function(schema) {
	        EpisodeResource.query({discharged: true}, function(resources) {
		        var episodes = {};
		        _.each(resources, function(resource) {
		            episodes[resource.id] = new Episode(resource, schema);
		        });
		        deferred.resolve(episodes);
	        }, function() {
		        // handle error better
		        $window.alert('Episodes could not be loaded');
	        });
	    });
	    return deferred.promise;
    };
});


services.factory('episodeLoader', function($q, $route,
                                           EpisodeResource,
                                           Episode, detailSchemaLoader) {
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

services.factory('episodeVisibility', function(){
    return function(episode, $scope, viewDischarged) {

        var location = episode.location[0];
        var demographics = episode.demographics[0];
        var hospital_number = $scope.query.hospital_number;
        var ward = $scope.query.ward;

        // Not active (no tags) - hide it.
        if(!episode.active && $scope.currentTag != 'mine' && !viewDischarged){
            return false;
        }

        // Not in the top level tag - hide it
	    if (location.tags[$scope.currentTag] != true) {
		    return false;
	    }

        // Not in the current subtag
	    if ($scope.currentSubTag != 'all' &&
            location.tags[$scope.currentSubTag] != true){
		    return false;
	    }

        // filtered out by hospital number
	    if (demographics.hospital_number &&
            demographics.hospital_number.toLowerCase().indexOf(
                hospital_number.toLowerCase()) == -1) {
		    return false;
	    }

        // Filtered out by ward.
        if (location.ward.toLowerCase().indexOf(ward.toLowerCase()) == -1) {
		    return false;
	    }
        return true;
	}
});

services.factory('Episode', function($http, $q, Item) {
    return function(resource, schema) {


        // AAAAAHCHAHK THIS COULD BREAK EVERYTHING:
        // TODO NOW - WE NEED A BETTER WAY TO PASS THE SCHEMA IN.
        schema = schema.default

	    var episode = this;
	    var column, field, attrs;
        // TODO - Pull these from the schema?
        var date_fields = ['date_of_admission', 'discharge_date'];

	    for (var cix = 0; cix < schema.getNumberOfColumns(); cix++) {
	        column = schema.columns[cix];
            if(resource[column.name]){
                var schemacol = _.findWhere(schema.columns, {name: column.name});
		        for (var iix = 0; iix < resource[column.name].length; iix++) {
		            attrs = resource[column.name][iix];
		            resource[column.name][iix] = new Item(attrs, episode, column);
		        };
                // Now we've instantiated, see if we want to sort
                // by any particular field
                if(schemacol.sort){
                    resource[column.name] = _.sortBy(resource[column.name],
                                                     schemacol.sort).reverse();
                }
            }
	    };
        // Sort a particular column according to schema params.
        this.sortColumn = function(columnName, sortBy){
            episode[columnName] = _.sortBy(episode[columnName], sortBy).reverse();
        }

        // Constructor to update from attrs and parse datish fields
        this.initialise = function(attrs){
            angular.extend(episode, attrs)
            // Convert string-serialised dates into native JavaScriptz
            _.each(date_fields, function(field){
                if(attrs[field]){
                    var parsed = moment(attrs[field], 'YYYY-MM-DD');
                    episode[field] = parsed._d;
                }
            });
        }

	    this.getNumberOfItems = function(columnName) {
	        return episode[columnName].length;
	    };

        // Getter function to return active episode tags.
        // Default implementation just hits location.
        this.getTags = function(){
            return _.keys(this.location[0].tags);
        };

	    this.newItem = function(columnName, opts) {
            if(!opts.schema){
                opts.schema = schema;
            }

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
            if (columnName == 'microbiology_input'){
                attrs.initials = window.initials
            }
            if (columnName == 'line'){
                attrs.inserted_by = window.initials
            }
	        return new Item(attrs, episode, opts.schema.getColumn(columnName));
	    };

	    this.getItem = function(columnName, iix) {
	        return episode[columnName][iix];
	    };

	    this.addItem = function(item) {
	        episode[item.columnName].push(item);
            if(item.sort){
                this.sortColumn(item.columnName, item.sort);
            }
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

        this.makeCopy = function(){
            var copy = {
                id               : episode.id,
                date_of_admission: episode.date_of_admission,
                discharge_date   : episode.discharge_date,
                consistency_token: episode.consistency_token
            }
            return copy
        };

	    this.compare = function(other) {
	        var v1, v2;
	        var comparators = [
		        function(p) { return CATEGORIES.indexOf(p.location[0].category) },
		        function(p) { return p.location[0].hospital },
		        function(p) {
		            if (p.location[0].hospital == 'UC4H' &&
                        p.location[0].ward.match(/^T\d+/)) {
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

        //
        //  Save our Episode.
        //
        //  1. Convert datey values to server-style
        //  2. Send our data to the server
        //  3. Handle the response.
        //
        this.save = function(attrs){
            var value;
            var deferred = $q.defer();
            var url = '/episode/' + attrs.id + '/';
            method = 'put'

            _.each(date_fields, function(field){
                if(attrs[field]){
                    if(angular.isString(attrs[field])){
                        value = moment(attrs[field], 'DD/MM/YYYY')
                    }else{
                        value = moment(attrs[field])
                    }
                    attrs[field] = value.format('YYYY-MM-DD');
                }
            });

            $http[method](url, attrs).then(
                function(response){
                    episode.initialise(response.data);
		            deferred.resolve();
                },
                function(response) {
		            // TODO handle error better
		            if (response.status == 409) {
			            alert('Item could not be saved because somebody else has \
recently changed it - refresh the page and try again');
		            } else {
			            alert('Item could not be saved');
		            };
		        }
            );

            return deferred.promise;
        };

        this.initialise(resource)
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
		        if (field.type == 'date' && item[field.name] &&  !_.isDate(item[field.name])) {
		            // Convert values of date fields to Date objects
		            item[field.name] = moment(item[field.name], 'YYYY-MM-DD')._d;
		        };
	        };
	    };

	    this.columnName = columnSchema.name;
        this.sort = columnSchema.sort

        // TODO: FTWLarry? What is this used for?
	    this.episodeName = episode.demographics ? episode.demographics[0].name : '';

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

        //
        // Save our Item to the server
        //
	    this.save = function(attrs) {
	        var field, value;
	        var deferred = $q.defer();
	        var url = '/' + this.columnName + '/';
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
		            alert('Item could not be saved because somebody else has \
recently changed it - refresh the page and try again');
		        } else {
		            alert('Item could not be saved');
		        };
	        });
	        return deferred.promise;
	    };

	    this.destroy = function() {
	        var deferred = $q.defer();
	        var url = '/' + item.columnName + '/' + item.id + '/';

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


services.factory('UserProfile', function($q, $http, $window) {
    var deferred = $q.defer();
    $http.get('/userprofile/').then(function(response) {
	    deferred.resolve(response.data);
    }, function() {
	    // handle error better
	    $window.alert('UserProfile could not be loaded');
    });
    return deferred.promise;
});

services.factory('FilterResource', function($resource) {
    return $resource('/filters/:id/', {id: '@id'});
});

services.factory('filtersLoader', function($q, $window, FilterResource, Filter) {
    return function(){
        var deferred =  $q.defer();
        FilterResource.query(function(resources){
            var filters = _.map(resources, function(resource){
                return new Filter(resource);
            });
            deferred.resolve(filters)
        }, function(){
            $window.alert('Filters could not be loaded')
        });
        return deferred.promise
    };
});

services.factory('Filter', function($http, $q) {
    return function(resource){
        var filter = this;

        this.initialise = function(attrs){
            angular.extend(filter, attrs);
        }

        this.save = function(attrs){
            var url = '/filters/';
            var deferred = $q.defer();
            var method;

	        if (angular.isDefined(filter.id)) {
		        method = 'put';
		        url += attrs.id + '/';
	        } else {
		        method = 'post';
	        }


            $http[method](url, attrs).then(
                function(response){
                    filter.initialise(response.data);
                    deferred.resolve(filter);
                },
                function(response) {
		            // TODO handle error better
		            if (response.status == 409) {
			            alert('Item could not be saved because somebody else has \
recently changed it - refresh the page and try again');
		            } else {
			            alert('Item could not be saved');
		            };
		        }
            );
            return deferred.promise;
        };

        this.destroy = function(){
	        var deferred = $q.defer();
	        var url = '/filters/' + item.id + '/';

	        $http['delete'](url).then(function(response) {
		        deferred.resolve();
	        }, function(response) {
		        // handle error better
		        alert('Item could not be deleted');
	        });
	        return deferred.promise;

        }

        this.initialise(resource);
    };
});
