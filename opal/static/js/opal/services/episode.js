angular.module('opal.services')
    .factory('Episode', function($http, $q, Item) {
    return function(resource, schema) {

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
            }else{
                resource[column.name] = [];
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
            return _.keys(this.location[0].tagging);
        };


        this.hasTag = function(tag){
            return _.has(this.getTags, tag);
        }

	    this.newItem = function(columnName, opts) {
            if(!opts){
                opts = {};
            }
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
