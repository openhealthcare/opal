// TODO:
// Make sure all modals now have error handlers.
//
var controllers = angular.module('opal.controllers', [
	'ngCookies',
	'opal.services',
	'ui.event',
	'ui.bootstrap',
    'mgcrea.ngStrap.typeahead',
    'mgcrea.ngStrap.helpers.dimensions',
    'mgcrea.ngStrap.tooltip',
    'mgcrea.ngStrap.helpers.dateParser',
    'mgcrea.ngStrap.datepicker',
]);

controllers.controller('RootCtrl', function($scope) {
	$scope.keydown = function(e) {
		$scope.$broadcast('keydown', e);
	};
});

controllers.controller('EpisodeListCtrl', function($scope, $q, $http, $cookieStore,
                                                   $location, $routeParams,
                                                   $modal,
                                                   Episode, schema, episodes, options,
                                                   profile,
                                                   episodeVisibility, viewDischarged){
    var version = window.version;
    if($cookieStore.get('opal.seenVersion') !=  version){
        $('#changelogTooltip').tooltip('show');
        $('#changelog').on('hidden.bs.modal', function(){
            $cookieStore.put('opal.seenVersion', version)
            $('#changelogTooltip').tooltip('hide');
        });
    }

    $scope.state = 'normal';
    console.log($scope.state)

	$scope.rix = 0; // row index
	$scope.cix = 0; // column index
	$scope.iix = 0; // item index

	$scope.mouseRix = -1; // index of row mouse is currently over
	$scope.mouseCix = -1; // index of column mouse is currently over
    $scope._ =  _;

	$scope.query = {hospital_number: '', name: ''};

    if(!$routeParams.tag){
        var tag =  $cookieStore.get('opal.currentTag') || 'mine';
        $location.path("/list/" + tag);
        return
    }
    $scope.currentTag = $routeParams.tag;

    if(!$routeParams.subtag){
        $scope.currentSubTag = 'all';
    }else{
        $scope.currentSubTag = $routeParams.subtag;
    }
    $scope.columns = schema.columns;


    $scope.profile = profile;

	$scope.rows = getVisibleEpisodes();
    $scope.tag_display = options.tag_display;

    $scope.episode_lookup = {};
    _.each(episodes,  function(e){
        if(e.location){         // Shouldn't be needed but occasionally happens in migration breakage
        _.each(e.location[0].tags, function(value, key){
            if(!_.has($scope.episode_lookup, key)){
                $scope.episode_lookup[key] = [];
            };
            $scope.episode_lookup[key].push(e.id);
        })
            }
    });

	function getVisibleEpisodes() {
		var visibleEpisodes = [];
        var episode_list;

        if($scope.episode_lookup){
            if($scope.currentSubTag == 'all'){
                episode_list = $scope.episode_lookup[$scope.currentTag];
            }else{
                episode_list = $scope.episode_lookup[$scope.currentSubTag];
            }
        }else{
            episode_list = [];
        }

        visibleEpisodes = _.map(
            _.filter(episode_list, function(id){
                return episodeVisibility(episodes[id], $scope, viewDischarged)
            }),
            function(id){
                return episodes[id];
            })
		visibleEpisodes.sort(compareEpisodes);
		return visibleEpisodes;
	};

	function compareEpisodes(p1, p2) {
		return p1.compare(p2);
	};

    $scope.jumpToTag = function(tag){
        if(_.contains(_.keys(options.tag_hierarchy), tag)){
            if($scope.currentTag == tag){
                $scope.currentSubTag = 'all';
            }else{
                $scope.currentTag = tag;
            }
            return;
        }else{
            for(var prop in options.tag_hierarchy){
                if(options.tag_hierarchy.hasOwnProperty(prop)){
                    if(_.contains(_.values(options.tag_hierarchy[prop]), tag)){
                        if($scope.currentTag == prop){
                            $scope.currentSubTag = tag;
                        }else{
                            $scope.nextSubTag = tag;
                            $scope.currentTag = prop;
                        }
                    }
                }
            }
        }
    }

    $scope.otherTags = function(item){
        var active = $scope.currentSubTag == 'all'?
            $scope.currentTag : $scope.currentSubTag;

        return _.filter(_.keys(item.tags), function(tag){
            if(tag == active){
                return false;
            }
            return true;
        });
    }

	$scope.$watch('currentTag', function() {
		$cookieStore.put('opal.currentTag', $scope.currentTag);
        if($scope.currentTag != $routeParams.tag){
            $scope.state = 'reloading'
        }
        $location.path('/list/' +  $scope.currentTag);
	});

	$scope.$watch('currentSubTag', function(){
		$cookieStore.put('opal.currentSubTag', $scope.currentSubTag);
        if($scope.currentSubTag == 'all'){
            if($routeParams.subtag && $scope.currentSubTag != $routeParams.subtag){
                $scope.state = 'reloading'
            }
            $location.path('/list/' +  $scope.currentTag);
        }else{
            if($scope.currentSubTag != $routeParams.subtag){
                $scope.state = 'reloading'
            }
            $location.path('/list/' +  $scope.currentTag + '/' +  $scope.currentSubTag);
        }
	});

    $scope.showSubtags = function(withsubtags){
        var show =  _.contains(withsubtags, $scope.currentTag);
        return show
    };

	$scope.$watch('query.hospital_number', function() {
		$scope.rows = getVisibleEpisodes();
	});

	$scope.$watch('query.name', function() {
		$scope.rows = getVisibleEpisodes();
	});

	$scope.$on('keydown', function(event, e) {
		if ($scope.state == 'normal') {
			switch (e.keyCode) {
			case 37: // left
				goLeft();
				break;
			case 39: // right
				goRight();
				break;
			case 38: // up
				goUp();
				break;
			case 40: // down
				goDown();
				break;
			case 13: // enter
			case 113: // F2
				$scope.editItem($scope.rix, $scope.cix, $scope.iix);
                e.preventDefault();
				break;
			case 8: // backspace
				e.preventDefault();
			case 46: // delete
				$scope.deleteItem($scope.rix, $scope.cix, $scope.iix);
				break;
			case 191: // question mark
				if(e.shiftKey){
					showKeyboardShortcuts();
				}
				break;
            case 78: // n
                $scope.addEpisode();
                e.preventDefault();
                break;
			};
		};
	});

	function getColumnName(cix) {
		return $scope.columns[cix].name;
	};

	function getRowIxFromEpisodeId(episodeId) {
		for (var rix = 0; rix < $scope.rows.length; rix++) {
			if ($scope.rows[rix].id == episodeId) {
				return rix;
			}
		};
		return -1;
	};

	function getEpisode(rix) {
		return $scope.rows[rix];
	};

	$scope.print = function() {
		window.print();
	};

	$scope.selectItem = function(rix, cix, iix) {
		$scope.rix = rix;
		$scope.cix = cix;
		$scope.iix = iix;
	};

	$scope.focusOnQuery = function() {
		$scope.selectItem(-1, -1, -1);
		$scope.state = 'search';
	};

	$scope.blurOnQuery = function() {
		if ($scope.rix == -1) {
			$scope.selectItem(0, 0, 0);
		};
		$scope.state = 'normal';
	};

	$scope.addEpisode = function() {
        if(profile.readonly){
            return null;
        };
		var hospitalNumberModal;

		$scope.state = 'modal';

		hospitalNumberModal = $modal.open({
			templateUrl: '/templates/modals/hospital_number.html/',
			controller: 'HospitalNumberCtrl',
            resolve: {
                schema: function(){ return schema },
                options: function(){ return options },
                tags: function(){ return {tag: $scope.currentTag,
                                          subtag: $scope.currentSubTag}}
            }
		}).result.then(
            function(episode) {
		        // User has either retrieved an existing episode or created a new one,
		        // or has cancelled the process at some point.
		        //
		        // This ensures that the relevant episode is added to the table and
		        // selected.
		        var rowIx;
		        $scope.state = 'normal';
		        if (episode) {
			        episodes[episode.id] = episode;
                    if($scope.episode_lookup[$scope.currentTag] === undefined){
                        $scope.episode_lookup[$scope.currentTag] = [];
                    }
                    $scope.episode_lookup[$scope.currentTag].push(episode.id);
                    if($scope.currentSubTag != 'all'){
                        $scope.episode_lookup[$scope.currentSubTag].push(episode.id)
                    }
			        $scope.rows = getVisibleEpisodes();
			        rowIx = getRowIxFromEpisodeId(episode.id);
			        $scope.selectItem(rowIx, 0, 0);
		        };
	        },
            function(reason){
                // The modal has been dismissed. Practically speaking this means
                // that the Angular UI called dismiss rather than our cancel()
                // method on the OPAL controller. We just need to re-set in order
                // to re-enable keybard listeners.
                $scope.state = 'normal';
            });
	};

	$scope.dischargeEpisode = function(rix, event) {
		var modal;
		var episode = getEpisode(rix);

        if(profile.readonly){
            return null;
        };

		// This is required to prevent the page reloading
		event.preventDefault();

		$scope.state = 'modal';

		modal = $modal.open({
			templateUrl: '/templates/modals/discharge_episode.html/',
			controller: 'DischargeEpisodeCtrl',
			resolve: {
				episode: function() { return episode; },
				currentTag: function() { return $scope.currentTag; },
                currentSubTag: function() { return $scope.currentSubTag; }
			}
		}).result.then(function(result) {
			$scope.state = 'normal';

			if (result == 'discharged') {
				$scope.rows = getVisibleEpisodes();
				$scope.selectItem(0, $scope.cix, 0);
			};
		});
	};

    // TODO: Test This!
    $scope.removeFromMine = function(rix, event){
        if(profile.readonly){
            return null;
        };

        event.preventDefault();

        var modal;
        var episode = getEpisode(rix);
        var location = episode.location[0];
        editing = location.makeCopy();
        delete editing.tags.mine;
        location.save(editing).then(function(result){
            $scope.rows = getVisibleEpisodes();
        })

    };

	$scope.editItem = function(rix, cix, iix) {
		var modal;
		var columnName = getColumnName(cix);
		var episode = getEpisode(rix);
		var item;

        if(profile.readonly){
            return null;
        };

		if (iix == episode.getNumberOfItems(columnName)) {
			item = episode.newItem(columnName, {schema: schema});
		} else {
			item = episode.getItem(columnName, iix);
		};

		$scope.selectItem(rix, cix, iix);
		$scope.state = 'modal';

		modal = $modal.open({
			templateUrl: '/templates/modals/' + columnName + '.html/',
			controller: 'EditItemCtrl',
			resolve: {
				item: function() { return item; },
				options: function() { return options; },
                episode: function() { return episode; }
			}
		});

		modal.result.then(function(result) {
			$scope.state = 'normal';

			if (columnName == 'location') {
				// User may have removed current tag
				$scope.rows = getVisibleEpisodes();
				$scope.selectItem(getRowIxFromEpisodeId(episode.id), $scope.cix, 0);
			}

			if (result == 'save-and-add-another') {
				$scope.editItem(rix, cix, episode.getNumberOfItems(columnName));
			};
		});
	};

	$scope.deleteItem = function(rix, cix, iix) {
		var modal;
		var columnName = getColumnName(cix);
		var episode = getEpisode(rix);
		var item = episode.getItem(columnName, iix);

        if(profile.readonly){
            return null;
        };

		if (schema.isSingleton(columnName)) {
			// Cannot delete singleton
			return;
		}

		if (!angular.isDefined(item)) {
			// Cannot delete 'Add'
			return;
		}

		$scope.state = 'modal'
		modal = $modal.open({
			templateUrl: '/templates/modals/delete_item_confirmation.html/',
			controller: 'DeleteItemConfirmationCtrl',
			resolve: {
				item: function() { return item; }
			}
		});

		modal.result.then(function(result) {
			$scope.state = 'normal';
		});
	};

	$scope.mouseEnter = function(rix, cix) {
		$scope.mouseRix = rix;
		$scope.mouseCix = cix;
	}

	$scope.mouseLeave = function() {
		$scope.mouseRix = -1;
		$scope.mouseCix = -1;
	}

    function showKeyboardShortcuts(){
		// TODO fix this
        $('#keyboard-shortcuts').modal();
    };

	function goLeft() {
		if ($scope.cix > 0) {
			$scope.cix--;
			$scope.iix = 0;
		};
	};

	function goRight() {
		if ($scope.cix < $scope.columns.length - 1) {
			$scope.cix++;
			$scope.iix = 0;
		};
	};

	function goUp() {
		var episode;
		var columnName = getColumnName($scope.cix);

		if ($scope.iix > 0) {
			$scope.iix--;
		} else if ($scope.rix > 0) {
			$scope.rix--;
			if (schema.isSingleton(columnName)) {
				$scope.iix = 0;
			} else {
				episode = getEpisode($scope.rix);
				$scope.iix = episode.getNumberOfItems(columnName);
			};
		};
	};

	function goDown() {
		var episode = getEpisode($scope.rix);
		var columnName = getColumnName($scope.cix);

		if (!schema.isSingleton(columnName) &&
		    ($scope.iix < episode.getNumberOfItems(columnName))) {
			$scope.iix++;
		} else if ($scope.rix < $scope.rows.length - 1) {
			$scope.rix++;
			$scope.iix = 0;
		};
	};
});

controllers.controller('EpisodeDetailCtrl', function($scope, $modal, $cookieStore,
                                                     schema,
                                                     episode, options, profile) {
    $scope._ = _;
	$scope.state = 'normal';

	$scope.cix = 0; // column index
	$scope.iix = 0; // item index

	$scope.mouseCix = -1; // index of column mouse is currently over

	$scope.episode = episode;
    $scope.profile =  profile;

	$scope.columns = schema.columns;
    $scope.tag_display = options.tag_display;

	$scope.$on('keydown', function(event, e) {
		if ($scope.state == 'normal') {
			switch (e.keyCode) {
			case 38: // up
				goUp();
				break;
			case 40: // down
				goDown();
				break;
			case 13: // enter
			case 113: // F2
				$scope.editItem($scope.cix, $scope.iix);
				break;
			case 8: // backspace
				e.preventDefault();
			case 46: // delete
				$scope.deleteItem($scope.cix, $scope.iix);
				break;
			case 191: // question mark
				if(e.shiftKey){
					showKeyboardShortcuts();
				}
				break;
			};
		};
	});

	function getColumnName(cix) {
		return $scope.columns[cix].name;
	};

	$scope.selectItem = function(cix, iix) {
		$scope.cix = cix;
		$scope.iix = iix;
	};

	$scope.editItem = function(cix, iix) {
		var modal;
		var columnName = getColumnName(cix);
		var item;

        if(profile.readonly){
            return null;
        };

		if (iix == episode.getNumberOfItems(columnName)) {
			item = episode.newItem(columnName);
		} else {
			item = episode.getItem(columnName, iix);
		}

		$scope.selectItem(cix, iix);
		$scope.state = 'modal';

		modal = $modal.open({
			templateUrl: '/templates/modals/' + columnName + '.html/',
			controller: 'EditItemCtrl',
			resolve: {
				item: function() { return item; },
				options: function() { return options; },
                episode: function() { return $scope.episode }
			}
		}).result.then(function(result) {
			$scope.state = 'normal';

			if (result == 'save-and-add-another') {
				$scope.editItem(cix, episode.getNumberOfItems(columnName));
			};
		});
	};

	$scope.deleteItem = function(cix, iix) {
		var modal;
		var columnName = getColumnName(cix);
		var item = episode.getItem(columnName, iix);

        if(profile.readonly){
            return null;
        };

		if (schema.isSingleton(columnName)) {
			// Cannot delete singleton
			return;
		}
		if (!angular.isDefined(item)) {
			// Cannot delete 'Add'
			return;
		}

		$scope.state = 'modal'
		modal = $modal.open({
			templateUrl: '/templates/modals/delete_item_confirmation.html/',
			controller: 'DeleteItemConfirmationCtrl',
			resolve: {
				item: function() { return item; }
			}
		}).result.then(function(result) {
			$scope.state = 'normal';
		});
	};

	$scope.mouseEnter = function(cix) {
		$scope.mouseCix = cix;
	}

	$scope.mouseLeave = function() {
		$scope.mouseCix = -1;
	}

	function goUp() {
		var columnName;

		if ($scope.iix > 0) {
			$scope.iix--;
		} else {
			if ($scope.cix > 0) {
				$scope.cix--;
				columnName = getColumnName($scope.cix);
				if (schema.isSingleton(columnName)) {
					$scope.iix = 0;
				} else {
					$scope.iix = episode.getNumberOfItems(columnName);
				};
			};
		};
	};

	function goDown() {
		var columnName = getColumnName($scope.cix);

		if (!schema.isSingleton(columnName) &&
		    ($scope.iix < episode.getNumberOfItems(columnName))) {
			$scope.iix++;
		} else if ($scope.cix < $scope.columns.length - 1) {
			$scope.cix++;
			$scope.iix = 0;
		};
	};

	$scope.dischargeEpisode = function(event) {
		var modal;
		var episode = $scope.episode;

        if(profile.readonly){
            return null;
        };

		// This is required to prevent the page reloading
		event.preventDefault();

		$scope.state = 'modal';

		modal = $modal.open({
			templateUrl: '/templates/modals/discharge_episode.html/',
			controller: 'DischargeEpisodeCtrl',
			resolve: {
				episode: function() { return episode; },
				currentTag: function() { return $scope.currentTag; },
				currentSubTag: function() { return $scope.currentSubTag; }
			}
		}).result.then(function(result) {
			$scope.state = 'normal';
		});
	};

    $scope.jumpToTag = function(tag){
        var currentTag, currentSubTag;

        currentTag = $cookieStore.get('opal.currentTag') || 'mine';
        currentSubTag = $cookieStore.get('opal.currentSubTag') || 'all';

        if(_.contains(_.keys(options.tag_hierarchy), tag)){
            $cookieStore.put('opal.currentTag', tag)
        }else{
            for(var prop in options.tag_hierarchy){
                if(options.tag_hierarchy.hasOwnProperty(prop)){
                    if(_.contains(_.values(options.tag_hierarchy[prop]), tag)){

                        $cookieStore.put('opal.currentTag', prop);
                        $cookieStore.put('opal.nextSubTag', tag);
                    }
                }
            }
        }
        // Jump to scope.
        window.location.hash = '#/'
    }
});

controllers.controller('SearchCtrl', function($scope, $http, $location, $modal,
                                              $q, Episode,
                                              schema, options) {
	$scope.searchTerms = {
		hospital_number: '',
		name: ''
	};
	$scope.results = [];
	$scope.searched = false;

	$scope.episode_category_list = ['OPAT', 'Inpatient', 'Outpatient', 'Review'];
	$scope.hospital_list = ['Heart Hospital', 'NHNN', 'UCH'];

	// $timeout(function() {
	// 	dialog.modalEl.find('input,textarea').first().focus();
	// });

	$scope.search = function() {
		var queryParams = [];
		var queryString;

		for (var term in $scope.searchTerms) {
			if ($scope.searchTerms[term] != '') {
				queryParams.push(term + '=' + $scope.searchTerms[term]);
			};
		};

		if (queryParams.length == 0) {
			return;
		};

		queryString = queryParams.join('&');

		$http.get('patient/?' + queryString).success(function(results) {
			$scope.searched = true;
			$scope.results = results;
		});
	};

    $scope.getEpisodeID = function(patient){
        var epid = patient.active_episode_id;
        if(!epid){
            epid = _.first(_.keys(patient.episodes));
        }
        return epid;
    }


	$scope.addEpisode = function() {
		var hospitalNumberModal;

		$scope.state = 'modal';

		hospitalNumberModal = $modal.open({
			templateUrl: '/templates/modals/hospital_number.html/',
			controller: 'HospitalNumberCtrl',
            resolve: {
                schema: function(){ return schema },
                options: function(){ return options },
                tags: function(){ return {tag: 'mine', subtag: 'all'}}}
		}).result.then(
            function(episode) {
			    // User has either retrieved an existing episode or created a new one,
			    // or has cancelled the process at some point.
			    //
			    // This ensures that the relevant episode is added to the table and
			    // selected.
			    $scope.state = 'normal';
			    if (episode) {
                    window.location.href = '#/episode/' + episode.id;
			    };
		    },
            function(reason){
                $scope.state = 'normal';
            }
        );
	};

});

controllers.controller(
    'HospitalNumberCtrl',
    function($scope,
             $timeout,
             $modal,
             $modalInstance,
             $http,
             $q,
             Episode,
             schema,
             options,
             tags) {

        // TODO- reimplement this
	    // $timeout(function() {
	    // 	dialog.modalEl.find('input,textarea').first().focus();
	    // });

        $scope.model = {}
        $scope.tags = tags;

	    $scope.findByHospitalNumber = function() {
            var deferred = $q.defer();
            var result = {
				patients: [],
				hospitalNumber: $scope.model.hospitalNumber
			};

            deferred.promise.then($scope.addForHospitalNumber);

            if($scope.model.hospitalNumber){
			    // The user entered a hospital number
			    $http.get('patient/?hospital_number=' + $scope.model.hospitalNumber)
                    .success(function(response) {
					    // We have retrieved patient records matching the hospital number
					    result.patients = response;
                        deferred.resolve(result);
				    });
            }else{
                deferred.resolve(result);
            }
	    };

        $scope.addForHospitalNumber = function(result){
		    if (result.patients.length == 0) {
                $scope.newPatient(result);
		    } else if (result.patients.length == 1) {
			    // There is a single patient with this hospital number
                $scope.newForPatient(result.patients[0]);
		    } else {
			    // This shouldn't happen, but we should probably handle it better
			    alert('ERROR: More than one patient found with hospital number');
			    $modalInstance.close(null);
		    };
        };

        $scope.newPatient = function(result){
			// There is no patient with this hospital number
			// Show user the form for creating a new episode,
            // with the hospital number pre-populated
			modal = $modal.open({
				templateUrl: '/templates/modals/add_episode.html/',
				controller: 'AddEpisodeCtrl',
				resolve: {
					schema: function() { return schema; },
					options: function() { return options; },
					demographics: function() {
						return { hospital_number: result.hospitalNumber }
					}
				}
			}).result.then(function(result) {
				// The user has created the episode, or cancelled
				$modalInstance.close(result);
			});
        };

        $scope.newForPatient = function(patient){
			if (patient.active_episode_id) {
				// This patient has an active episode
                $scope.newForPatientWithActiveEpisode(patient);
			} else { // This patient has no active episode
                // Check to see if the patient has *any* episodes
                if (_.keys(patient.episodes).length ==  0){
                    $scope.addForPatient(patient);
                }else {
					// Convert episodes to Episodes - TODO
                    // it'd be better if this happened when the patient
                    // was retrieved
					for (var eix in patient.episodes) {
						patient.episodes[eix] = new Episode(patient.episodes[eix],
                                                            schema);
					}
					// Ask user if they want to reopen an episode, or open a new one
					modal = $modal.open({
						templateUrl: '/templates/modals/reopen_episode.html/',
						controller: 'ReopenEpisodeCtrl',
						resolve: {
							patient: function() { return patient; },
							tag: function() { return $scope.tags.tag; }
						}
					}).result.then(function(result) {
						var demographics;
						if (result == 'open-new') {
							// User has chosen to open a new episode
                            $scope.addForPatient(patient);
						} else {
							// User has chosen to reopen an episode, or cancelled
							$modalInstance.close(result);
						};
					});
                }
			};
        };

        $scope.newForPatientWithActiveEpisode = function(patient){
			episode = new Episode(patient.episodes[patient.active_episode_id],
                                  schema)
			if (episode.location[0].tags[$scope.tags.tag] &&
                ($scope.tags.subtag == 'all' ||
                 episode.location[0].tags[$scope.tags.subtag])) {
				// There is already an active episode for this patient
                // with the current tag
				$modalInstance.close(episode);
			} else {
				// There is already an active episode for this patient but
                // it doesn't have the current tag.
                // Add the current Tag.
                episode.location[0].tags[$scope.tags.tag] = true;
                if($scope.tags.subtag != 'all'){
                    episode.location[0].tags[$scope.tags.subtag] = true;
                }
                episode.location[0].save(episode.location[0].makeCopy()).then(
                    function(){
				        $modalInstance.close(episode);
                    });
			}
        };

        $scope.addForPatient = function(patient){
            demographics = patient.demographics[0];
            if(demographics.date_of_birth){
                var dob = moment(demographics.date_of_birth, 'YYYY-MM-DD')
                    .format('DD/MM/YYYY');
				demographics.date_of_birth = dob;
            }

            modal = $modal.open({
				templateUrl: '/templates/modals/add_episode.html/',
				controller: 'AddEpisodeCtrl',
				resolve: {
					schema: function() { return schema; },
					options: function() { return options; },
					demographics: function() { return demographics; }
				}
			}).result.then(function(result){
                $modalInstance.close(result);
            });
        };

	    $scope.cancel = function() {
		    $modalInstance.close(null);
	    };

    });


controllers.controller('AddEpisodeCtrl', function($scope, $http, $cookieStore,
                                                  $timeout,
                                                  $modalInstance, Episode, schema,
                                                  options,
                                                  demographics) {
	$scope.currentTag = $cookieStore.get('opal.currentTag') || 'mine';
	$scope.currentSubTag = $cookieStore.get('opal.currentSubTag') || 'all';

    // TODO - find a way to reimplement this
	// $timeout(function() {
	// 	dialog.modalEl.find('input,textarea').first().focus();
	// });


	for (var name in options) {
		$scope[name + '_list'] = options[name];
	};

	$scope.episode_category_list = ['OPAT', 'Inpatient', 'Outpatient', 'Review'];

    // TODO - this is no longer the way location/admission date works.
	$scope.editing = {
		date_of_admission: moment().format('DD/MM/YYYY'),
		location: {
			tags: {},
            hospital: 'UCLH'
		},
		demographics: demographics
	};
	$scope.editing.location.tags[$scope.currentTag] = true;
	if($scope.currentSubTag != 'all'){
		$scope.editing.location.tags[$scope.currentSubTag] = true;
	}

	$scope.showSubtags = function(withsubtags){
		var show =  _.some(withsubtags, function(tag){
            return $scope.editing.location.tags[tag]
        });
		return show
	};

	$scope.save = function() {
		var value;

		// This is a bit mucky but will do for now
        // TODO - this is obviously broken now that location is not like this.
		value = $scope.editing.date_of_admission;
		if (value) {
            var doa = moment(value, 'DD/MM/YYYY').format('YYYY-MM-DD');
			$scope.editing.date_of_admission = doa;
		}

		value = $scope.editing.demographics.date_of_birth;
		if (value) {
            var dob = moment(value, 'DD/MM/YYYY').format('YYYY-MM-DD');
			$scope.editing.demographics.date_of_birth = dob;
		}

		$http.post('episode/', $scope.editing).success(function(episode) {
			episode = new Episode(episode, schema);
			$modalInstance.close(episode);
		});
	};

	$scope.cancel = function() {
		$modalInstance.close(null);
	};
});

controllers.controller('ReopenEpisodeCtrl', function($scope, $http, $timeout,
                                                     $modalInstance, patient, tag) {
    // TODO: Reimplement this.
    //
	// $timeout(function() {
	// 	dialog.modalEl.find('input,textarea').first().focus();
	// });

	$scope.episodes = _.values(patient.episodes);
	$scope.model = {episodeId: 'None'};

    $scope.sortEpisodes = function(e1, e2) {
		var date1 = e1.date_of_admission;
		var date2 = e2.date_of_admission;

		if (angular.isUndefined(date1)) {
			return -1;
		} else if (angular.isUndefined(date2)) {
			return 1;
		} else if (date1 < date2) {
			return -1;
		} else if (date2 < date1) {
			return 1;
		} else {
			return 0;
		};
	}

	$scope.episodes.sort($scope.sortEpisodes);

	$scope.openNew = function() {
		$modalInstance.close('open-new');
	};

	$scope.reopen = function() {
		var episode = patient.episodes[parseInt($scope.model.episodeId, 10)];
		var location = episode.getItem('location', 0);
		var attrs = location.makeCopy();

		attrs.tags[tag] = true;
		location.save(attrs).then(function(result) {
            episode.save(episode.makeCopy()).then(function(result){
			    $modalInstance.close(episode);
            });
		});
	};
});

controllers.controller('EditItemCtrl', function($scope, $cookieStore, $timeout,
                                                $modalInstance,
                                                item, options, episode) {
    $scope.episode = episode.makeCopy();
	$scope.editing = item.makeCopy();
    $scope.state = 'editing';

    // TODO: FTWLarry? What is this used for?
	$scope.editingName = item.episodeName;

    $scope.columnName = item.columnName;
    // initially display episodes of interest to current user
    $scope.currentTag = $cookieStore.get('opal.currentTag') || 'mine';
    // initially display episodes of interest to current user
    $scope.currentSubTag = 'all';

    $scope.showSubtags = function(withsubtags){
	    if (item.columnName == 'location') {
		    return _.some(withsubtags, function(tag){ return item.tags[tag] });
	    } else {
		    return false;
	    };
    };

    // TODO - reimplement this
	// $timeout(function() {
	// 	$modalInstance.modalEl.find('input,textarea').first().focus();
	// });

	for (var name in options) {
		if (name.indexOf('micro_test') != 0) {
			$scope[name + '_list'] = options[name];
		};
	};

	if (item.columnName == 'microbiology_test') {
		$scope.microbiology_test_list = [];
		$scope.microbiology_test_lookup = {};
		$scope.micro_test_defaults =  options.micro_test_defaults;

		for (var name in options) {
			if (name.indexOf('micro_test') == 0) {
				for (var ix = 0; ix < options[name].length; ix++) {
					$scope.microbiology_test_list.push(options[name][ix]);
					$scope.microbiology_test_lookup[options[name][ix]] = name;
				};
			};
		};

		$scope.$watch('editing.test', function(testName) {
			$scope.testType = $scope.microbiology_test_lookup[testName];
            if( _.isUndefined(testName) || _.isUndefined($scope.testType) ){
                return;
            }
            if($scope.testType in $scope.micro_test_defaults){
                _.each(
                    _.pairs($scope.micro_test_defaults[$scope.testType]),
                    function(values){
                        var field =  values[0];
                        var _default =  values[1];
                        var val = _default
                        if($scope.editing[field]){
                            val = $scope.editing[field]
                        }
                        $scope.editing[field] =  val;
                    });
            }
		});
	};

	$scope.episode_category_list = ['OPAT',  'Inpatient', 'Outpatient', 'Review'];

	$scope.save = function(result) {
        $scope.state = 'saving';
		item.save($scope.editing).then(function() {
            if($scope.columnName == 'location'){
                episode.save($scope.episode).then(function(){
                    $modalInstance.close(result)
                });
            }else{
			    $modalInstance.close(result);
            }
		});
	};

	$scope.cancel = function() {
		$modalInstance.close('cancel');
	};
});

controllers.controller('DeleteItemConfirmationCtrl', function($scope, $timeout,
                                                              $modalInstance, item) {
    // TODO: Reimplement this!
    //
	// $timeout(function() {
	// 	dialog.modalEl.find('button.btn-primary').first().focus();
	// });

	$scope.destroy = function() {
		item.destroy().then(function() {
			$modalInstance.close('deleted');
		});
	};

	$scope.cancel = function() {
		$modalInstance.close('cancel');
	};
});

controllers.controller('ExtractCtrl', function($scope, $http, $window, $modal,
                                               filters, options, schema){
    $scope.JSON = window.JSON;
    $scope.state =  'normal';
    $scope.filters = filters;
    $scope.columns = schema.columns;
    $scope.column_names = _.map(schema.columns, function(c){
        return c.name.underscoreToCapWords();
    });

	for (var name in options) {
		$scope[name + '_list'] = options[name];
	};

    $scope.model = {
        combine  : "and",
        column   : null,
        field    : null,
        queryType: "Equals",
        query    : null
    };

    $scope.criteria = [_.clone($scope.model)];

    $scope.searchableFields = function(column){
        // TODO - don't hard-code this
        if(column.name == 'microbiology_test'){
            return [
                'Test',
                'Date Ordered',
                'Details',
                'Microscopy',
                'Organism',
                'Sensitive Antibiotics',
                'Resistant Antibiotics'
            ]
        }
        return _.map(
            _.reject(
                column.fields,
                function(c){ return c.type == 'token' ||  c.type ==  'list'; }),
            function(c){ return c.name.underscoreToCapWords(); }
        );
    };

    $scope.isType = function(column, field, type){
        if(!column || !field){
            return false;
        }
        var col = _.find($scope.columns, function(item){return item.name == column.toLowerCase().replace( / /g,  '_')});
        var theField =  _.find(col.fields, function(f){return f.name == field.toLowerCase().replace( / /g,  '_')});
        return theField.type == type;
    };

    $scope.isBoolean = function(column, field){
        return $scope.isType(column, field, "boolean");
    };

    $scope.isText = function(column, field){
        return $scope.isType(column, field, "string") || $scope.isType(column, field, "text");
    }

    $scope.isDate = function(column, field){
        return $scope.isType(column, field, "date");
    };

    $scope.addFilter = function(){
        $scope.criteria.push(_.clone($scope.model));
    };

    $scope.removeFilter = function(index){
        $scope.criteria.splice(index, 1);
    };

    $scope.search = function(){
        $scope.state = 'pending';
        $http.post('/search/extract/', $scope.criteria).success(
            function(results){
                $scope.results = results;
                $scope.state = 'normal';
            }).error(function(){
                $scope.state = 'normal';
                $window.alert('ERROR: Could not process this search. Please report it to the OPAL team')
            });
    };

    $scope.jumpToFilter = function($event, filter){
        $event.preventDefault()
        $scope.criteria = filter.criteria;
    }

    $scope.editFilter = function($event, filter, $index){
        $event.preventDefault();
		modal = $modal.open({
			templateUrl: '/templates/modals/save_filter_modal.html/',
			controller: 'SaveFilterCtrl',
			resolve: {
				params: function() { return $scope.filters[$index]; },
			}
		}).result.then(function(result){
            $scope.filters[$index] = result;
        });
    }

    $scope.save = function(){

		modal = $modal.open({
			templateUrl: '/templates/modals/save_filter_modal.html/',
			controller: 'SaveFilterCtrl',
			resolve: {
				params: function() { return {name: null, criteria: $scope.criteria}; },
			}
		}).result.then(function(result){
            $scope.filters.push(result);
        });
    };

});

controllers.controller('SaveFilterCtrl', function($scope, $modalInstance, Filter, params) {
    $scope.state = 'editing';
    $scope.model = params;

	$scope.save = function(result) {
        $scope.state = 'saving';
        var filter = new Filter($scope.model);
		filter.save($scope.model).then(function(result) {
			$modalInstance.close(result);
		});
	};


	$scope.cancel = function() {
		$modalInstance.close('cancel');
	};

})
