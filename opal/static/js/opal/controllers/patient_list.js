angular.module('opal.controllers').controller(
    'PatientListCtrl', function($scope, $q, $http, $cookies,
                                $location, $routeParams,
                                $modal, $rootScope, $window, $injector,
                                growl, Flow, Item, Episode,
                                episodedata, metadata, profile, episodeVisibility){

        $scope.ready = false;
        var version = window.version;
        if(episodedata.status == 'error'){
            if($cookies.get('opal.previousPatientList')){
                $cookies.remove('opal.previousPatientList');
                $location.path('/list/')
                return
            }
            $window.location.href = '/404';
            return
        }else{
            $scope.episodes = episodedata.data;
            $rootScope.state = 'normal';
            $scope.url = $location.url();
            $scope.metadata = metadata;
            $scope.listView = true;

            $scope.num_episodes = _.keys($scope.episodes).length;

  	        $scope.rix = 0; // row index
            $scope._ =  _;

  	        $scope.query = {
                hospital_number: '', first_name: '', surname: '', ward: '', bed: ''
            };
            $scope.$location = $location;
            $scope.path_base = '/list/';
            $scope.profile = profile;

            $cookies.put('opal.previousPatientList', $routeParams.slug);
            var tags = $routeParams.slug.split('-')
            $scope.currentTag = tags[0];
            $scope.currentSubTag = tags.length == 2 ? tags[1] : "";
            $scope.tag_display = metadata.tag_display;
            var pertinantTag = $scope.currentSubTag || $scope.currentTag;

            //
            // These are used for setting custom list sort orders
            //
            $scope.comparators = null;

            if($scope.metadata.patient_list_comparators &&
               _.has($scope.metadata.patient_list_comparators, $routeParams.slug)){
                $scope.comparators = $injector.get(
                    $scope.metadata.patient_list_comparators[$routeParams.slug]
                );
            }
        }

	    $scope.compareEpisodes = function(p1, p2) {
            if($scope.comparators){
                return p1.compare(p2, $scope.comparators);
            }else{
                return p1.compare(p2);
            }
	    };

	    $scope.getVisibleEpisodes = function() {
		    var visibleEpisodes = [];
        var episode_list = [];
        var episodePresent;

        visibleEpisodes = _.filter($scope.episodes, function(episode){
            return episodeVisibility(episode, $scope);
        });

    		visibleEpisodes.sort($scope.compareEpisodes);

        if($scope.rows && visibleEpisodes.length){
          if($scope.episode){
            episodePresent = _.any(visibleEpisodes, function(x){
                return x.id === $scope.episode.id;
            });
          }

          if(!episodePresent){
              $scope.select_episode(visibleEpisodes[0], 0);
          }
        }
    		return visibleEpisodes;
	    };

	    $scope.rows = $scope.getVisibleEpisodes();
        $scope.episode = $scope.rows[0];

        $scope.ready = true;

        //
        // This is used to be callable we can pass to
        // the table row iterator in the spreadsheet template.
        //
        $scope.isSelectedEpisode = function(episode){
            return episode === $scope.episode;
        }

        $scope.editTags = function(){
            $rootScope.state = 'modal';
            $scope.open_modal(
                'EditTeamsCtrl',
                '/templates/modals/edit_teams.html',
                {episode: $scope.episode}
            ).then(function(){
                if(!$scope.episode.hasTag(pertinantTag)){
                    delete $scope.episodes[$scope.episode.id];
                    $scope.rows = _.filter($scope.rows, function(e){
                        return e.id !== $scope.episode.id;
                    });
                }
                $rootScope.state = 'normal';
                $scope.episode = $scope.rows[0];
            });
        };

        $scope.jumpToEpisodeDetail = function(episode){
            $location.url(episode.link);
        }

        $scope.jumpToTag = function(tag){
            if(_.contains(_.keys(metadata.tag_hierarchy), tag)){
                $location.path($scope.path_base + tag)
            }else{
                for(var prop in metadata.tag_hierarchy){
                    if(metadata.tag_hierarchy.hasOwnProperty(prop)){
                        if(_.contains(_.values(metadata.tag_hierarchy[prop]), tag)){
                            $location.path($scope.path_base + prop + '-' + tag)
                        }
                    }
                }
            };
        }

	    $scope.$watch('query.hospital_number', function() {
		    $scope.rows = $scope.getVisibleEpisodes();
	    });

	    $scope.$watch('query.ward', function() {
		    $scope.rows = $scope.getVisibleEpisodes();
	    });

	    $scope.$watch('query.bed', function() {
		    $scope.rows = $scope.getVisibleEpisodes();
	    });

	    $scope.$watch('query.name', function() {
		    $scope.rows = $scope.getVisibleEpisodes();
	    });

	    $scope.$on('keydown', function(event, e) {
		    if ($rootScope.state == 'normal') {
			    switch (e.keyCode) {
                case 191: // question mark
                    if(e.shiftKey){
                        $scope.keyboard_shortcuts();
                    }
                    break;
                case 13:
                    if(profile.can_see_pid()){
                        $scope.jumpToEpisodeDetail($scope.episode);
                    }
                    break;
    			case 38: // up
    				goUp();
    				break;
    			case 40: // down
    				goDown();
    				break;
                case 78: // n
                    $scope.addEpisode();
    		    }
            }
	    });

	    $scope.getRowIxFromEpisodeId = function(episodeId) {
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
		    $window.print();
	    };

	    $scope.focusOnQuery = function() {
		    $rootScope.state = 'search';
	    };

	    $scope.blurOnQuery = function() {
		    $rootScope.state = 'normal';
	    };

	    $scope.addEpisode = function() {
            if(profile.readonly){ return null; };

            var enter = Flow.enter(
                {
                    current_tags: {
                        tag: $scope.currentTag,
                        subtag: $scope.currentSubTag
                    }
                },
                $scope
            );

            $rootScope.state = 'modal';
            enter.then(
                function(resolved) {
		            // We have either retrieved an existing episode or created a new one,
                    // rendered a new modal for which we are waiting,
		            // or has cancelled the process at some point.

                    var return_to_normal = function(episode){
                    	// This ensures that the relevant episode is added to the table and
		                // selected.
		                var rowIx;
		                $rootScope.state = 'normal';
  		                if (episode && episode != 'cancel') {
                            //
                            // Occasionally the addPatient modal will add an episode to a list we're
                            // not currently on. So we check to see if they're tagged to this list.
                            //
                            if(episode.tagging[0][$scope.currentTag]){
                                if(!$scope.currentSubTag || episode.tagging[0][$scope.currentSubTag]){
  			                        $scope.episodes[episode.id] = episode;
  			                        $scope.rows = $scope.getVisibleEpisodes();
  			                        rowIx = $scope.getRowIxFromEpisodeId(episode.id);
                                    $scope.num_episodes += 1;
                                }
                            }
                            var msg = episode.demographics[0].first_name + " " + episode.demographics[0].surname;
                            var newTags = _.intersection(_.keys(episode.tagging[0]), _.keys(metadata.tags));
                            var newTag;

                            if(newTags.length > 1){
                                var tagObjs = _.filter(metadata.tags, function(t){ return _.contains(newTags, t.name); });
                                if($scope.currentSubTag.length){
                                    newTag = _.findWhere(tagObjs, {parent_tag: $scope.currentTag}).name;
                                }
                                else{
                                    newTag = _.findWhere(tagObjs, {name: $scope.currentTag}).name;
                                }
                            }
                            else{
                                newTag = newTags[0];
                            }
                            msg += " added to the " + metadata.tags[newTag].display_name + " list";
                            growl.success(msg);

  		                }
                    };
                    if(resolved && resolved.then){ // OMG - it's a promise!
                        resolved.then(
                            function(r){ return_to_normal(r) },
                            function(r){ return_to_normal(r) }
                        );
                    }else{
                        return_to_normal(resolved);
                    }
	            },
                function(reason){
                    // The modal has been dismissed. Practically speaking this means
                    // that the Angular UI called dismiss rather than our cancel()
                    // method on the OPAL controller. We just need to re-set in order
                    // to re-enable keybard listeners.
                    $rootScope.state = 'normal';
                });
	    };

        $scope.removeFromList = function(episode_id){
            delete $scope.episodes[episode_id];
            $scope.rows = $scope.getVisibleEpisodes();
            $scope.num_episodes -= 1;
            $scope.episode = $scope.rows[0];
        }

        $scope._post_discharge = function(result, episode){
    		$rootScope.state = 'normal';
      		if (result == 'discharged' | result == 'moved') {
                  $scope.removeFromList(episode.id);
      		};
        };

	    $scope.dischargeEpisode = function(episode) {
            if(profile.readonly){ return null; };

		    $rootScope.state = 'modal';
            var exit = Flow.exit(episode,
                {
                    current_tags: {
                        tag   : $scope.currentTag,
                        subtag: $scope.currentSubTag
                    },
                },
                $scope
            );

            exit.then(function(result) {
                //
                // Sometimes our Flow will open another modal - we wait for that
                // to close before firing the Post discharge hooks - this avoids the list
                // scope from trapping keystrokes etc
                //
                if(result && result.then){
                    result.then(function(r){
                        $scope._post_discharge(r, episode);
                    });
                }else{
                    $scope._post_discharge(result, episode);
                }
		    });
	    };

        $scope.removeFromMine = function(episode){
            if(profile.readonly){
                return null;
            }

            var modal;
            var tagging = episode.tagging[0];
            editing = tagging.makeCopy();
            editing.mine = false;
            // console.error('calling tagging save');
            // console.error(tagging.save);
            tagging.save(editing).then(function(){
                $scope.removeFromList(episode.id);
            });

        };

        $scope.newNamedItem = function(episode, name) {
            return episode.recordEditor.newItem(name);
        };

        $scope.is_tag_visible_in_list = function(tag){
            return _.contains(metadata.tag_visible_in_list, tag);
        };

        $scope.editNamedItem  = function(episode, name, iix) {
            var reset_state = function(result){
                if (name == 'tagging') {
                    // User may have removed current tag
                    $scope.rows = $scope.getVisibleEpisodes();
                }
                var item = _.last(episode[name]);

                if (episode[name].sort){
                    episode.sortColumn(item.columnName, item.sort);
                }
            };

            episode.recordEditor.editItem(name, iix).then(function(result){
                reset_state(result);
            });
        };

	    function goUp() {
		    var episode;
            if ($scope.rix > 0) {
			    $scope.rix--;
				$scope.episode = getEpisode($scope.rix);
		    };
	    };

	    function goDown() {
		    var episode = getEpisode($scope.rix);
            if ($scope.rix < $scope.rows.length - 1) {
			    $scope.rix++;
                $scope.episode = $scope.rows[$scope.rix];
		    };
	    };

        $scope.select_episode = function(episode, rix){
            $scope.episode = episode;
            $scope.rix = rix;
        }

        $scope.keyboard_shortcuts = function(){
            $modal.open({
                controller: "KeyBoardShortcutsCtrl",
                templateUrl: 'list_keyboard_shortcuts.html'
            })
        }
    });
