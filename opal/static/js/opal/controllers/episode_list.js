angular.module('opal.controllers').controller(
    'EpisodeListCtrl', function($scope, $q, $http, $cookieStore,
                                $location, $routeParams,
                                $modal, $rootScope,
                                $window,
                                growl,
                                Flow, Item,
                                Episode, episodes, options,
                                profile, episodeVisibility){
        $scope.ready = false;
        var version = window.version;
        $rootScope.state = 'normal';
        $scope.url = $location.url();

        $scope.options = options;
        $scope.listView = true;

        $scope.num_episodes = _.keys(episodes).length;

	    $scope.rix = 0; // row index
        $scope._ =  _;

  	    $scope.query = {hospital_number: '', name: '', ward: '', bed: ''};
        $scope.$location = $location;
        $scope.path_base = '/list/';
        $scope.currentTag = $routeParams.tag;

        if(!$routeParams.subtag){
            // this should never be the case, redirection should be done
            // by the episode list redirect controller
            if($scope.currentTag in options.tag_hierarchy &&
               options.tag_hierarchy[$scope.currentTag].length > 0){

                var subtag = $cookieStore.get('opal.currentSubTag') || "";

                if(!subtag){
                    subtag = options.tag_hierarchy[$scope.currentTag][0];
                }

                var target = $scope.path_base + $scope.currentTag + '/' + subtag;
                $location.path(target);
                $location.replace();
                return;
            }
        }

        $scope.currentSubTag = $routeParams.subtag || "";
        $scope.profile = profile;
        $scope.tag_display = options.tag_display;

	    $scope.getVisibleEpisodes = function() {
		    var visibleEpisodes = [];
        var episode_list = [];

        visibleEpisodes = _.filter(episodes, function(episode){
            return episodeVisibility(episode, $scope);
        });
		    visibleEpisodes.sort(compareEpisodes);
        if($scope.rows && visibleEpisodes.length == 1){
            rix = getRowIxFromEpisodeId(visibleEpisodes[0].id);
            $scope.select_episode(visibleEpisodes[0], rix);
        }
		    return visibleEpisodes;
	    };

	    $scope.rows = $scope.getVisibleEpisodes();
        $scope.episode = $scope.rows[0];

        $scope.ready = true;

        $scope.isSelectedEpisode = function(episode){
            return episode === $scope.episode;
        }

	    function compareEpisodes(p1, p2) {
		    return p1.compare(p2);
	    };

        $scope.jumpToTag = function(tag){
            if(_.contains(_.keys(options.tag_hierarchy), tag)){
                $location.path($scope.path_base + tag)
            }else{
                for(var prop in options.tag_hierarchy){
                    if(options.tag_hierarchy.hasOwnProperty(prop)){
                        if(_.contains(_.values(options.tag_hierarchy[prop]), tag)){
                            $location.path($scope.path_base + prop + '/' + tag)
                        }
                    }
                }

            };
        }

	    $scope.$watch('currentTag', function() {
		    $cookieStore.put('opal.currentTag', $scope.currentTag);
            if($scope.currentTag != $routeParams.tag){
                $$rootScope.state = 'reloading'
            }
            var target = $scope.path_base +  $scope.currentTag;

            $location.path(target);
	    });

	    $scope.$watch('currentSubTag', function(){
		    $cookieStore.put('opal.currentSubTag', $scope.currentSubTag);
            if($scope.currentSubTag == ''){
                if($routeParams.subtag && $scope.currentSubTag != $routeParams.subtag){
                    $rootScope.state = 'reloading'
                }
                $location.path($scope.path_base +  $scope.currentTag);
            }else{
                if($scope.currentSubTag != $routeParams.subtag){
                    $rootScope.state = 'reloading'
                }
                $location.path($scope.path_base +  $scope.currentTag + '/' +  $scope.currentSubTag);
            }
	    });

        $scope.showSubtags = function(withsubtags){
            var show =  _.contains(withsubtags, $scope.currentTag);
            return show
        };

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
                        $location.url($scope.episode.link);
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

        $scope.$on('change', function(event, episode) {
            episode = new Episode(episode);
            if(episodes[episode.id]){
                episodes[episode.id] = episode;
                var rix = getRowIxFromEpisodeId(episode.id);
                if(rix != -1){
                    $scope.rows[rix] = episode;
                }
            }
        });

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

	    $scope.focusOnQuery = function() {
		    $rootScope.state = 'search';
	    };

	    $scope.blurOnQuery = function() {
		    $rootScope.state = 'normal';
	    };

	    $scope.addEpisode = function() {
            if(profile.readonly){ return null; };

            var enter = Flow(
                'enter', options,
                {
                    current_tags: {
                        tag: $scope.currentTag,
                        subtag: $scope.currentSubTag
                    }
                }
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
  			                episodes[episode.id] = episode;
  			                $scope.rows = $scope.getVisibleEpisodes();
  			                rowIx = getRowIxFromEpisodeId(episode.id);
                            $scope.num_episodes += 1;
                            var readableName = $scope.tag_display[$scope.currentSubTag];
                            var msg = episode.demographics[0].name + " added to the " + readableName + " list";
                            growl.success(msg);

  		                }
                    };

                    if(resolved.then){ // OMG - it's a promise!
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

      $scope._post_discharge = function(result){
  			$rootScope.state = 'normal';
  			if (result == 'discharged' | result == 'moved') {
  				$scope.rows = $scope.getVisibleEpisodes();
          $scope.num_episodes -= 1;
  			};
      };

	    $scope.dischargeEpisode = function(episode) {
            if(profile.readonly){ return null; };

		    $rootScope.state = 'modal';

            var exit = Flow(
                'exit', options,
                {
                    current_tags: {
                        tag   : $scope.currentTag,
                        subtag: $scope.currentSubTag
                    },
                    episode: episode
                }
            );

            exit.then(function(result) {
                //
                // Sometimes our Flow will open another modal - we wait for that
                // to close before firing the Post discharge hooks - this avoids the list
                // scope from trapping keystrokes etc
                //
                if(result && result.then){
                    result.then(function(r){ $scope._post_discharge(r); });
                }else{
                    $scope._post_discharge(result);
                }
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
            var tagging = episode.tagging[0];
            editing = tagging.makeCopy();
            editing.mine = false;
            tagging.save(editing).then(function(result){
                $scope.rows = $scope.getVisibleEpisodes();
            })
        };

        $scope.newNamedItem = function(episode, name) {
            return episode.recordEditor.newItem(name, {tag: $scope.currentTag, subTag: $scope.subTag});
        }

        $scope.is_tag_visible_in_list = function(tag){
            return _.contains(options.tag_visible_in_list, tag);
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

            episode.recordEditor.editItem(name, iix, {tag: $scope.currentTag, subtag: $scope.currentSubTag}).then(function(result){
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
            if(rix == $scope.rix){
                return true;
            }else{
                $scope.episode = episode;
                $scope.rix = rix;
            }
            return true;
        }

        $scope.controller_for_episode = function(controller, template, size, episode){
            $modal.open({
                controller : controller,
                templateUrl: template,
                size       : size,
                resolve    : {
                    episode: function(){ return episode }
                }
            });
        }

        $scope.keyboard_shortcuts = function(){
            $modal.open({
                controller: "KeyBoardShortcutsCtrl",
                templateUrl: 'list_keyboard_shortcuts.html'
            })
        }
    });
