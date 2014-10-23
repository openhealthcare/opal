angular.module('opal.controllers').controller(
    'EpisodeListCtrl', function($scope, $q, $http, $cookieStore,
                                $location, $routeParams,
                                $modal, $rootScope,
                                Flow, Item,
                                Episode, schema, episodes, options,
                                profile,
                                episodeVisibility, viewDischarged){

        var version = window.version;
        $scope.state = 'normal';
        $scope.url = $location.url()

	    $scope.rix = 0; // row index
	    $scope.cix = 0; // column index
	    $scope.iix = 0; // item index

	    $scope.mouseRix = -1; // index of row mouse is currently over
	    $scope.mouseCix = -1; // index of column mouse is currently over
        $scope._ =  _;

	    $scope.query = {hospital_number: '', name: '', ward: '', bed: ''};
        
        if(viewDischarged){
            $scope.path_base = '/discharge/';
        }else{
            $scope.path_base = '/list/';
        }

        if(!$routeParams.tag){
            var tag =  $cookieStore.get('opal.currentTag') || _.keys(options.tag_hierarchy)[0];
            $location.path($scope.path_base + tag);
            return
        }
        $scope.currentTag = $routeParams.tag;

        if(!$routeParams.subtag){
            // We now force redirect to the first subtag if there is one
            if($scope.currentTag in options.tag_hierarchy &&
               options.tag_hierarchy[$scope.currentTag].length > 0){
                var subtag = options.tag_hierarchy[$scope.currentTag][0];
                var target = $scope.path_base + $scope.currentTag + '/' + subtag;
                $location.path(target);
                return
            }else{
                $scope.currentSubTag = 'all';
            }
        }else{
            $scope.currentSubTag = $routeParams.subtag;
        }
        $scope.columns = schema.columns;

        $scope.profile = profile;
        $scope.tag_display = options.tag_display;

	    function getVisibleEpisodes() {
		    var visibleEpisodes = [];
            var episode_list = [];

            visibleEpisodes = _.filter(episodes, function(episode){
                return episodeVisibility(episode, $scope, viewDischarged)
            });
		    visibleEpisodes.sort(compareEpisodes);
		    return visibleEpisodes;
	    };

	    $scope.rows = getVisibleEpisodes();

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

        $scope.otherTags = function(episode){
            tags = episode.getTags();
            return _.filter(tags, function(t){
                if(t in options.tag_hierarchy &&
                   options.tag_hierarchy[t].length > 0){ return false };
                if(t == $scope.currentTag){ return false };
                if(t == $scope.currentSubTag){ return false };
                return true
            });
        }

	    $scope.$watch('currentTag', function() {
		    $cookieStore.put('opal.currentTag', $scope.currentTag);
            if($scope.currentTag != $routeParams.tag){
                $scope.state = 'reloading'
            }
            var target = $scope.path_base +  $scope.currentTag;

            $location.path(target);
	    });

	    $scope.$watch('currentSubTag', function(){
		    $cookieStore.put('opal.currentSubTag', $scope.currentSubTag);
            if($scope.currentSubTag == 'all'){
                if($routeParams.subtag && $scope.currentSubTag != $routeParams.subtag){
                    $scope.state = 'reloading'
                }
                $location.path($scope.path_base +  $scope.currentTag);
            }else{
                if($scope.currentSubTag != $routeParams.subtag){
                    $scope.state = 'reloading'
                }
                $location.path($scope.path_base +  $scope.currentTag + '/' +  $scope.currentSubTag);
            }
	    });

        $scope.showSubtags = function(withsubtags){
            var show =  _.contains(withsubtags, $scope.currentTag);
            return show
        };

	    $scope.$watch('query.hospital_number', function() {
		    $scope.rows = getVisibleEpisodes();
	    });
	    $scope.$watch('query.ward', function() {
		    $scope.rows = getVisibleEpisodes();
	    });
	    $scope.$watch('query.bed', function() {
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
            if(profile.readonly){ return null; };

            var enter = Flow(
                'enter', schema, options,
                {
                    current_tags: {
                        tag: $scope.currentTag,
                        subtag: $scope.currentSubTag
                    }
                }
            );

		    $scope.state = 'modal';

            enter.then(
                function(episode) {
		            // User has either retrieved an existing episode or created a new one,
		            // or has cancelled the process at some point.
		            //
		            // This ensures that the relevant episode is added to the table and
		            // selected.
		            var rowIx;
		            $scope.state = 'normal';
		            if (episode && episode != 'cancel') {
			            episodes[episode.id] = episode;
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
		    var episode = getEpisode(rix);

            if(profile.readonly){ return null; };

		    event.preventDefault();// Required to prevent the page reloading
		    $scope.state = 'modal';

            var exit = Flow(
                'exit', schema, options,
                {
                    current_tags: {
                        tag   : $scope.currentTag,
                        subtag: $scope.currentSubTag
                    },
                    episode: episode
                }
            );

            exit.then(function(result) {
			    $scope.state = 'normal';

			    if (result == 'discharged' | result == 'moved') {
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
            var tagging = episode.tagging[0];
            editing = tagging.makeCopy();
            editing.mine = false;
            tagging.save(editing).then(function(result){
                $scope.rows = getVisibleEpisodes();
            })

        };

      _openEditItemModal = function(item, columnName, episode) {
        if(profile.readonly){
          return null;
        };
        $scope.state = 'modal';

        modal = $modal.open({
          templateUrl: '/templates/modals/' + columnName + '.html/',
          controller: 'EditItemCtrl',
          resolve: {
            item: function() { return item; },
            options: function() { return options; },
            profile: function() { return profile; },
            episode: function() { return episode; }
          }
        });

        modal.result.then(function(result) {
          $scope.state = 'normal';

          if (columnName == 'tagging') {
            // User may have removed current tag
            $scope.rows = getVisibleEpisodes();
            $scope.selectItem(getRowIxFromEpisodeId(episode.id), $scope.cix, 0);
          }

          if (result == 'save-and-add-another') {
            $scope.editItem(rix, cix, episode.getNumberOfItems(columnName));
          };
                if (item.sort){
                    episode.sortColumn(item.columnName, item.sort);
                };
        }, function(){
                $scope.state = 'normal';
            });
      }

      $scope.newNamedItem = function(episode, name) {
        var item = episode.newItem(name, {column: $rootScope.fields[name]});
        if (!episode[name]) {
          episode[name] = [];
        }
        episode[name][0] = item;
        _openEditItemModal(item, name, episode);
      }

      $scope.editNamedItem = function(episode, name, iix) {
        var item;
        if (episode[name][iix] && episode[name][iix].columnName) {
          item = episode[name][iix];
        } else {
          item = new Item(episode[name][iix], episode, $rootScope.fields[name]);
          episode[name][iix] = item;
        }

        _openEditItemModal(item, name, episode);
      }

	    $scope.editItem = function(rix, cix, iix) {
		    var modal;
		    var columnName = getColumnName(cix);
		    var episode = getEpisode(rix);
		    var item;

            if(columnName == 'demographics' && !profile.can_see_pid()){
                return false;
            }
            
		    if (iix == episode.getNumberOfItems(columnName)) {
			    item = episode.newItem(columnName, {schema: schema});
		    } else {
			    item = episode.getItem(columnName, iix);
		    };

		    $scope.selectItem(rix, cix, iix);
        _openEditItemModal(item, columnName, episode);
	    };

	    $scope.deleteItem = function(rix, cix, iix) {
		    var modal;
		    var columnName = getColumnName(cix);
		    var episode = getEpisode(rix);
		    var item = episode.getItem(columnName, iix);

            if(profile.readonly){
                return null;
            };

            if (schema.isReadOnly(columnName)) {
                // Cannont delete readonly columns
                return;
            }

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
    });
