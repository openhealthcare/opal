//
// This is the main Episode class for Opal
//
angular.module('opal.services')
    .factory('Episode', function(
        $http, $q, $rootScope, $window,
        Item, RecordEditor) {
        "use strict";

        // TODO: Set this with a more idiomatic Angular way, and set it once.
        var DATE_FORMAT = 'DD/MM/YYYY';
        var Episode = function(resource) {
            this.initialise(resource);

        }

        // TODO - Pull these from the schema? Also cast them to moments
        // Note - these are date fields on the episode itself - which is not currently
        // serialised and sent with the schema !
        var date_fields = ['start', 'end'];

        Episode.prototype = {
            // Constructor to update from attrs and parse datish fields
            initialise: function(data){
                var self = this;
                // We would like a way to open a modal that edits subrecords.
                self.recordEditor = new RecordEditor(self); // TODO: Rename or refactor this.

                // We would like everything for which we have data that is a field to
                // be an instantiated instance of Item
                _.each($rootScope.fields, function(field){
                    if(data[field.name]){
                        data[field.name] = _.map(
                            data[field.name],
                            function(attrs){ return new Item(attrs, self, field); });
                        if(field.sort){
                            data[field.name] = _.sortBy(data[field.name], field.sort).reverse();
                        }
                    }else{ data[field.name] = []; }
                });
                angular.extend(self, data)
                _.each(date_fields, function(field){
                  if(data[field]){
                    self[field] = moment(data[field], DATE_FORMAT);
                  }
                });
                if(!self.demographics || self.demographics.length == 0 || !self.demographics[0].patient_id){
                    throw "Episode() initialization data must contain demographics with a patient id."
                }
                self.link = "/patient/" + self.demographics[0].patient_id + "/" + self.id;
            },

            // Sort a particular column according to schema params.
            sortColumn: function(columnName, sortBy){
                this[columnName] = _.sortBy(this[columnName], sortBy).reverse();
            },

            // Return the name of the patient suitable for display to humans
            getFullName: function(){
                return this.demographics[0].first_name + ' ' + this.demographics[0].surname;
            },

            // Getter function to return active episode tags.
            // Default implementation just hits tagging
            getTags: function(){
                var tags;

                if(this.tagging[0].makeCopy){
                    tags =  this.tagging[0].makeCopy();
                }else{
                    tags = this.tagging[0];
                }
                var tagKeys = _.keys(tags);
                tagKeys = _.filter(tagKeys, function(tagKey){
                  return tagKey !== "_client" && tagKey !== "id";
                });
                return _.filter(tagKeys,  function(t){return tags[t];});
            },

            //
            // Boolean predicate function to determine whether
            // this episode has the given TAG
            //
            hasTag: function(tag){
                return this.getTags().indexOf(tag) != -1;
            },

            //
            // Create a new Item of type COLUMNNAME
            //
            newItem: function(columnName, opts) {
                var self = this;
                if(!opts){ opts = {}; }

                if(!opts.column){
                    opts.column = $rootScope.fields[columnName];
                }

                var attrs = {};
                return new Item(attrs, self, opts.column);
            },

            getItem: function(columnName, iix) {
                return this[columnName][iix];
            },


            //
            // add an item (e.g. instance of a subrecord) to this episode
            //
            addItem: function(item) {
                // Sometimes we add an item from a non-active schema.
                // TODO: Do we really do this any more?
                if(!this[item.columnName]){
                    this[item.columnName] = [];
                }
                this[item.columnName].push(item);
                if(item.sort){
                    this.sortColumn(item.columnName, item.sort);
                }
            },

            removeItem: function(item) {
                var items = this[item.columnName];
                for (var iix = 0; iix < items.length; iix++) {
                    if (item.id == items[iix].id) {
                        items.splice(iix, 1);
                        break;
                    };
                };
            },

            makeCopy: function(){
                var start, end;
                /*
                * undefined is not serailised.
                * we explicitly set to null, to set
                * fields that were populated to null
                */
                if(this.start){
                  start = moment(this.start).toDate();
                }
                else{
                  start = null;
                }

                if(this.end){
                  end = moment(this.end).toDate();
                }
                else{
                  end = null;
                }
                var copy = {
                    id               : this.id,
                    category_name    : this.category_name,
                    consistency_token: this.consistency_token,
                    start: start,
                    end: end
                }
                return copy
            },

            compare: function(other, comparators) {
                var self = this;
                //
                // The default comparators we use for our Episode sorting in lists
                //
                var comparators = comparators || [
                    function(p) {
                      if(p.start){
                        // we want to order by -start date
                        return -p.start.toDate().getTime();
                      }
                    },
                    function(p) { return p.first_name },
                    function(p) { return p.surname }
                ];

                var v1, v2;
                for (var ix = 0; ix < comparators.length; ix++) {
                    v1 = comparators[ix](self);
                    v2 = comparators[ix](other);
                    if (v1 < v2) {
                        return -1;
                    } else if (v1 > v2) {
                        return 1;
                    }
                }

                return 0;
            },

            //
            //  Save our Episode.
            //
            //  1. Convert datey values to server-style
            //  2. Send our data to the server
            //  3. Handle the response.
            //
            save: function(attrs){
                var self = this;
                var value;
                var deferred = $q.defer();
                var url = '/api/v0.1/episode/' + attrs.id + '/';
                var method = 'put';

                _.each(date_fields, function(field){
                    if(attrs[field]){
                        value = attrs[field];

                        if(!angular.isString(attrs[field])){
                            value = moment(attrs[field]).format(DATE_FORMAT);
                        }

                        attrs[field] = value;
                    }
                });

                $http[method](url, attrs).then(
                    function(response){
                        self.initialise(response.data);
                        deferred.resolve();
                    },
                    function(response) {
                        // TODO handle error better
                        if (response.status == 409) {
                            $window.alert('Item could not be saved because somebody else has \
recently changed it - refresh the page and try again');
                        } else {
                            $window.alert('Item could not be saved');
                        };
                    }
                );

                return deferred.promise;
            },

        }; // Closes prototype

        return Episode

    });
