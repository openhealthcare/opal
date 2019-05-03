angular.module('opal.services')
    .factory('Item', function($http, $q, $injector, $window, FieldTranslator) {
        return function(attrs, episode, columnSchema) {
            var item = this;
            this.episode =  episode;
            this.formController = 'EditItemCtrl';

            this.initialise = function(attrs) {
                // Copy all attributes to item, and change any date fields to Date objects
                var field, value;

                _.each(columnSchema.fields, function(field){
                    delete item[field.name];
                });

                var toUpdate = FieldTranslator.subRecordToJs(attrs, columnSchema.name);
                angular.extend(item, toUpdate);
                if(columnSchema.angular_service){
                    var serv = $injector.get(columnSchema.angular_service);
                    serv(item);
                }
            };


            this.columnName = columnSchema.name;
            this.sort = columnSchema.sort;
            this.size = columnSchema.modal_size;

            this.isSingleton = function(){
                return columnSchema.single
            };

            this.isReadOnly = function(){
                return columnSchema.readOnly;
            };

            //
            // Returns a clone of the editable fields + consistency token so that
            // we can then update them in isolation elsewhere.
            //
            this.makeCopy = function() {
                var field, value;
                var copy = {id: item.id};
                copy._client = {id: _.uniqueId(item.columnName)};

                _.each(columnSchema.fields, function(field){
                    value = item[field.name];
                    if (field.type == 'date' && item[field.name]) {
                        // Convert values of date fields to strings of format DD/MM/YYYY
                        copy[field.name] = moment(value).toDate();
                    }else if(field.type == 'date_time' && item[field.name]) {
                        copy[field.name] = moment(value).toDate();
                    } else {
                        if(field.default && !item.id){
                            copy[field.name] = _.clone(field.default);
                        }
                        else{
                            copy[field.name] = _.clone(value);
                        }
                    }
                });

                return copy;
            };

            // casts to dates/datetimes to the format the server reads dates
            this.castToType = function(attrs){
                return FieldTranslator.jsToSubrecord(attrs, columnSchema.name);
            }

            //
            // Save our Item to the server
            //
            this.save = function(attrs) {
                var field, value;
                var deferred = $q.defer();
                var url = '/api/v0.1/' + this.columnName + '/';
                var method;
                delete attrs._client;
                attrs = this.castToType(attrs);

                // Tagging to teams are represented as a pseudo subrecord.
                // Fake the ID attribute so we can know what episode we're tagging to.
                //
                // We can't do this at initialization time because the episode has
                // not fully initialized itself at that point.
                // TODO: Refactor episode initialization.
                if (this.columnName == 'tagging') {
                    item.id = episode.id;
                    attrs.id = episode.id;
                }
                if (angular.isDefined(item.id)) {
                    method = 'put';
                    url += attrs.id + '/';
                } else {
                    method = 'post';
                    attrs.episode_id = episode.id;
                }
                $http[method](url, attrs).then(
                    function(response) {
                        item.initialise(response.data);
                        if (method == 'post') {
                            episode.addItem(item);
                        }
                        deferred.resolve();
                    },
                    function(response) {
                        // handle error better
                        if (response.status == 409) {
                            $window.alert('Item could not be saved because somebody else has \
recently changed it - refresh the page and try again');
                        } else {
                            $window.alert('Item could not be saved');
                        }
                        deferred.reject();
                    });
                return deferred.promise;
            };

	        this.destroy = function() {
	            var deferred = $q.defer();
	            var url = '/api/v0.1/' + item.columnName + '/' + item.id + '/';

	            $http['delete'](url).then(
                    function(response) {
		                episode.removeItem(item);
		                deferred.resolve();
	                },
                    function(response) {
		                // handle error better
		                $window.alert('Item could not be deleted');
	                });

	            return deferred.promise;
	        };

	        this.initialise(attrs);
        };
    });
