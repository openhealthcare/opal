angular.module('opal.services')
    .factory('Item', function($http, $q, $injector, FieldTranslater) {
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

                var toUpdate = FieldTranslater.subRecordToJs(attrs, columnSchema.name);
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

	            for (var fix = 0; fix < columnSchema.fields.length; fix++) {
		            field = columnSchema.fields[fix];
		            value = item[field.name];
		            if (field.type == 'date' && item[field.name]) {
		                // Convert values of date fields to strings of format DD/MM/YYYY
		                copy[field.name] = moment(value).toDate();
                    }else if(field.type == 'date_time' && item[field.name]) {
                        copy[field.name] = moment(value).toDate();
		            } else {
		                copy[field.name] = _.clone(value);
		            }
	            }

	            return copy;
	        };

            // casts to dates/datetimes to the format the server reads dates
            this.castToType = function(attrs){
                return FieldTranslater.jsToSubrecord(attrs, columnSchema.name);
            }

            //
            // Save our Item to the server
            //
	        this.save = function(attrs) {
	            var field, value;
	            var deferred = $q.defer();
	            var url = '/api/v0.1/' + this.columnName + '/';
	            var method;

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

	            $http[method](url, attrs).then(function(response) {
		            item.initialise(response.data);
		            if (method == 'post') {
		                episode.addItem(item);
		            }
		            deferred.resolve();
	            }, function(response) {
		            // handle error better
		            if (response.status == 409) {
		                alert('Item could not be saved because somebody else has \
recently changed it - refresh the page and try again');
		            } else {
		                alert('Item could not be saved');
		            }
                    deferred.reject();
	            });
	            return deferred.promise;
	        };

	        this.destroy = function() {
	            var deferred = $q.defer();
	            var url = '/api/v0.1/' + item.columnName + '/' + item.id + '/';

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
