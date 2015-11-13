angular.module('opal.services')
    .factory('EpisodeDetailMixin', function($rootScope, $modal, $location, $cookieStore, Item){
        return function($scope){

            var episode = $scope.episode;
            var profile = $scope.profile;
            var options = $scope.options;
            // var schema  = $scope.schema;
            var Flow    = $scope.Flow

	        $scope.selectItem = function(cix, iix) {
		        $scope.cix = cix;
		        $scope.iix = iix;
	        };

            _openEditItemModal = function(item, columnName){
                var modal;

                if(profile.readonly){
                    return null;
                };
                $rootScope.state = 'modal';

                var modal_opts = {
			        templateUrl: '/templates/modals/' + columnName + '.html/',
                    controller: 'EditItemCtrl',
                    resolve: {
                        item: function() { return item; },
                        options: function() { return options; },
                        profile: function() { return profile; },
                        episode: function() { return $scope.episode; }
                    }
                }

                if(item.size){
                    modal_opts.size = item.size;
                }

                modal = $modal.open(modal_opts);


                modal.result.then(function(result) {
			        $rootScope.state = 'normal';
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
                return _openEditItemModal(item, name)
            };

            $scope.newNamedItem = function(name) {
                var item = episode.newItem(name, {column: $rootScope.fields[name]});
                if (!episode[name]) {
                    episode[name] = [];
                }
                return _openEditItemModal(item, name);
            };

	        $scope.deleteItem = function(column_name, iix) {
		        var modal;
		        var item = episode.getItem(column_name, iix);

                if(profile.readonly){
                    return null;
                };

		        if (!angular.isDefined(item)) {
			        // Cannot delete 'Add'
			        return;
		        }

                if(!item.isReadOnly){
                    item = new Item(column_name, episode, $rootScope.fields[column_name]);
                }

                if (item.isReadOnly()) {
                    // Cannont delete readonly columns
                    return;
                }

		        if (item.isSingleton()) {
			        // Cannot delete singleton
			        return;
		        }

		        $rootScope.state = 'modal'
		        modal = $modal.open({
			        templateUrl: '/templates/modals/delete_item_confirmation.html/',
			        controller: 'DeleteItemConfirmationCtrl',
			        resolve: {
				        item: function() { return item; }
			        }
		        }).result.then(function(result) {
			        $rootScope.state = 'normal';
		        });
	        };

            $scope.deleteNamedItem = function(name, index){
                // TODO: Deprecate this fully - no longer neded !
                return $scope.deleteItem(name, index)
            };

	        $scope.mouseEnter = function(cix) {
		        $scope.mouseCix = cix;
	        }

	        $scope.mouseLeave = function() {
		        $scope.mouseCix = -1;
	        }

	        $scope.dischargeEpisode = function() {
                if(profile.readonly){ return null; };

		        $rootScope.state = 'modal';
                var exit = Flow(
                    'exit',
                    null,  // Schema ? Not used ? Todo: investigate!
                    options,
                    {
                        current_tags: {
                            tag   : $scope.currentTag,
                            subtag: $scope.currentSubTag
                        },
                        episode: $scope.episode
                    }
                );

                exit.then(function(result) {
			        $rootScope.state = 'normal';
		        });
	        };

            $scope.addEpisode = function(){
                if(profile.readonly){ return null; };

                var enter = Flow(
                    'enter', schema, options,
                    {
                        current_tags: { tag: 'mine', subtag: 'all' },
                        hospital_number: $scope.episode.demographics[0].hospital_number
                    }
                );

		        $rootScope.state = 'modal';

                enter.then(
                    function(episode) {
		                // User has either retrieved an existing episode or created a new one,
		                // or has cancelled the process at some point.
		                //
		                // This ensures that the relevant episode is added to the table and
		                // selected.
		                $rootScope.state = 'normal';
                        if(episode){
                            $location.path('/episode/' + episode.id);
                        }
	                },
                    function(reason){
                        // The modal has been dismissed. We just need to re-set in order
                        // to re-enable keybard listeners.
                        $rootScope.state = 'normal';
                    });
            },

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

        }
    });
