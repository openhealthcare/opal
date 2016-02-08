//
// This is the main Episode class for OPAL.
//
angular.module('opal.services')
    .factory('Episode', function($http, $q, $rootScope, $routeParams, Item) {
        Episode = function(resource) {

	        var episode = this;
	        var column, field, attrs;

            // We would like everything for which we have data that is a field to
            // be an instantiated instance of Item - not just those fields in the
            // currently applicable schema.
            _.each($rootScope.fields, function(field){
                if(resource[field.name]){
                    resource[field.name] = _.map(
                        resource[field.name],
                        function(attrs){ return new Item(attrs, episode, field); });
                    if(field.sort){
                        resource[field.name] = _.sortBy(resource[field.name], field.sort).reverse();
                    }
                }else{ resource[field.name] = []; }
            });

            // Sort a particular column according to schema params.
            this.sortColumn = function(columnName, sortBy){
                episode[columnName] = _.sortBy(episode[columnName], sortBy).reverse();
            }

            //
            // TODO - Pull these from the schema?
            // Note - these are date fields on the episode itself - which is not currently
            // serialised and sent with the schema !
            var date_fields = ['date_of_admission', 'discharge_date', 'date_of_episode'];

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
            // Default implementation just hits tagging
            this.getTags = function(){
                if(this.tagging[0].makeCopy){
                    var tags =  this.tagging[0].makeCopy()
                }else{
                    var tags = this.tagging[0]
                }
                delete tags.id
                return _.filter(_.keys(tags),  function(t){return tags[t]})
            };

            //
            // Boolean predicate function to determine whether
            // this episode has the given TAG
            //
            this.hasTag = function(tag){
                return this.getTags().indexOf(tag) != -1;
            }

            //
            // Return those tags that are child items in HIERARCHY
            //
            this.childTags = function(hierarchy){
                return _.filter(episode.getTags(), function(t){
                    if(t in hierarchy && hierarchy[t].length > 0){ return false };
                    return true
                });
            }

	        this.newItem = function(columnName, opts) {
                var column;

                if(!opts){ opts = {}; }

                if(!opts.column){
                    opts.column = $rootScope.fields[columnName];
                }

	            var attrs = {};
                //
	            // TODO: don't hardcode this
                //
                // TODO: For serious, this is a bad place for these to go.
                //
	            if (columnName == 'microbiology_test') {
		            attrs.date_ordered = moment().format('YYYY-MM-DD');
	            }
	            if (columnName == 'general_note') {
		            attrs.date = moment().format('YYYY-MM-DD');
	            }
	            if (columnName == 'diagnosis') {
		            attrs.date_of_diagnosis = moment().format('YYYY-MM-DD');
	            }
                if (columnName == 'microbiology_input'){
                    attrs.initials = window.initials;
		            attrs.when = new Date();
                }
                if (columnName == 'observation'){
                    attrs.datetime = new Date();
                }
                if (columnName == 'line'){
                    attrs.insertion_date = moment().format('YYYY-MM-DD');
                }
                if (columnName == 'opat_review'){
                    attrs.initials = window.initials;
                    attrs.datetime = new Date();
                }
                if (columnName == 'opat_line_assessment'){
                    attrs.assessment_date = moment().format('YYYY-MM-DD');
                }
                //
                // That's right, it gets worse!
                //
                if(columnName == 'antimicrobial'){
                    if($routeParams.tag == 'walkin'){
                        attrs.start_date = new Date();
                    }
                }
	            return new Item(attrs, episode, opts.column);
	        };

	        this.getItem = function(columnName, iix) {
	            return episode[columnName][iix];
	        };

            //
            // add an item (e.g. instance of a subfield) to this episode
            //
	        this.addItem = function(item) {
                // Sometimes we add an item from a non-active schema.
                if(!episode[item.columnName]){
                    episode[item.columnName] = [];
                }
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
                    category         : episode.category,
                    date_of_admission: episode.date_of_admission,
                    date_of_episode  : episode.date_of_episode,
                    discharge_date   : episode.discharge_date,
                    consistency_token: episode.consistency_token
                }
                return copy
            };

	        this.compare = function(other) {
              if($routeParams.tag === "walkin" && $routeParams.subtag === "walkin_review"){
                  var getName = function(x){
                      return x.demographics[0].name.toLowerCase();
                  };

                  if(other.date_of_episode > this.date_of_episode){
                      return -1;
                  }
                  else if(other.date_of_episode < this.date_of_episode){
                      return 1;
                  }
                  else if(getName(other) > getName(this)){
                      return -1;
                  }
                  else if(getName(other) < getName(this)){
                      return 1;
                  }

                  return 0;
              }
              else{
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
              }
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

            //
            // Predicate to determine whether this episode is discharged or not
            //
            this.isDischarged = function(){
                return episode.location[0].category == 'Discharged' ||
                    (episode.discharge_date && moment(episode.discharge_date).isBefore(moment()));
            }

            this.initialise(resource)
        };

        //
        // takes two arguments, the hospital number and a hash of callbacks.
        //
        // There are three cases for which we proceed:
        //
        // 1. A new patient
        // 2. An existing patient
        // 3. Failure
        //
        // These should be expressed as { newPatient: ..., newForPatient: ..., error: ... }
        //
        Episode.findByHospitalNumber = function(number, callbacks){
            var deferred = $q.defer();
            var result = {
				patients: [],
				hospitalNumber: number
			};

            deferred.promise.then(function(result){
                if(result.patients.length == 0){
                    callbacks.newPatient(result);
                }else if(result.patients.length == 1){
                    callbacks.newForPatient(result.patients[0])
                }else{
                    callbacks.error();
                }
            })

            if(number){
			    // The user entered a hospital number
			    $http.get('/search/patient/?hospital_number=' + number)
                    .success(function(response) {
					    // We have retrieved patient records matching the hospital number
					    result.patients = response;
                        deferred.resolve(result);
				    });
            }else{
                deferred.resolve(result);
            }


        }
        return Episode
    });
