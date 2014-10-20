angular.module('opal.controllers').controller(
    'EpisodeDetailCtrl', function($scope, $modal, $cookieStore, $location,
                                  $rootScope,
                                  Flow,
                                  schema,
                                  episode, options, profile) {
        $scope._ = _;
	    $scope.state = 'normal';

	    $scope.cix = 0; // column index
	    $scope.iix = 0; // item index

	    $scope.mouseCix = -1; // index of column mouse is currently over

	    $scope.episode = episode;
        $scope.total_episodes = 1 + episode.prev_episodes.length + episode.next_episodes.length;
        $scope.this_episode_number = episode.prev_episodes.length + 1;

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

        _openEditItemModal = function(item, columnName){
            var modal;

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
                    episode: function() { return $scope.episode }
			    }
		    }).result.then(function(result) {
			    $scope.state = 'normal';

			    if (result == 'save-and-add-another') {
				    $scope.editItem(cix, episode.getNumberOfItems(columnName));
			    };
		    });
        }

        $scope.editNamedItem = function(name, index){
            var item;
            if (episode[name][index] && episode[name][index].columnName) {
                item = episode[name][index];
            } else {
                item = new Item(episode[name][index], episode, $rootScope.fields[name]);
                episode[name][index] = item;
            }
            _openEditItemModal(item, name)
        };

        $scope.newNamedItem = function(name) {
            var item = episode.newItem(name, {column: $rootScope.fields[name]});
            if (!episode[name]) {
                episode[name] = [];
            }
            _openEditItemModal(item, name);            
        };
        
	    $scope.editItem = function(cix, iix) {
		    var columnName = getColumnName(cix);
		    var item;

		    if (iix == episode.getNumberOfItems(columnName)) {
			    item = episode.newItem(columnName);
		    } else {
			    item = episode.getItem(columnName, iix);
		    }

		    $scope.selectItem(cix, iix);
            _openEditItemModal(item, columnName, episode);
	    };

	    $scope.deleteItem = function(cix, iix) {
		    var modal;
		    var columnName = getColumnName(cix);
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
		    event.preventDefault(); // required to prevent the page reloading

            if(profile.readonly){ return null; };

		    $scope.state = 'modal';
            var exit = Flow(
                'exit', schema, options,
                {
                    current_tags: {
                        tag   : $scope.currentTag,
                        subtag: $scope.currentSubTag
                    },
                    episode: $scope.episode
                }
            );

            exit.then(function(result) {
			    $scope.state = 'normal';
		    });
	    };

        $scope.jumpToTag = function(tag){
            var currentTag, currentSubTag;

            currentTag = $cookieStore.get('opal.currentTag') || 'mine';
            currentSubTag = $cookieStore.get('opal.currentSubTag') || 'all';

            if(_.contains(_.keys(options.tag_hierarchy), tag)){
                $location.path('/list/'+tag)
                return
            }else{
                for(var prop in options.tag_hierarchy){
                    if(options.tag_hierarchy.hasOwnProperty(prop)){
                        if(_.contains(_.values(options.tag_hierarchy[prop]), tag)){
                            $location.path('/list/'+ prop + '/' + tag)
                            return
                        }
                    }
                }
            }
            // Jump to scope.
            window.location.hash = '#/'
        };

        $scope.controller_for_episode = function(controller, template, size){
            $modal.open({
                controller : controller, 
                templateUrl: template,
                size       : size,
                resolve    : {
                    episode: function(){ return $scope.episode }
                }
            });
        };

        $scope.historyModal = function(){
            console.log('displayhistory')
        };
        
    });
