angular.module('opal.controllers').controller(
  'PatientListCtrl', function($scope, $cookies,
                              $location, $routeParams,
                              $modal, $rootScope, $window, $injector, $q,
                              episodedata, metadata, profile, episodeLoader,
                              episodeVisibility){

    $scope.ready = false;
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
    // Reload a single episode from the server.
    // Useful for Pathway callbacks.
    //
    $scope.refresh = function(episode_id){
      var deferred = $q.defer();
      episodeLoader(episode_id).then(
        function(episode){
          $scope.episodes[episode_id] = episode;
          if($scope.episode.id == episode_id){
            $scope.episode = episode;
          }
          $scope.rows = $scope.getVisibleEpisodes();
          deferred.resolve();
        }
      )
      return deferred.promise;
    }

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
      }
    };

	$scope.$on('keydown', function(event, e) {
	  if ($rootScope.state == 'normal') {
		switch (e.keyCode) {
        case 191: // question mark
          if(e.shiftKey){
            $scope.keyboard_shortcuts();
          }
          break;
        case 13:
          $scope.jumpToEpisodeDetail($scope.episode);
          break;
    	case 38: // up
    	  goUp();
    	  break;
    	case 40: // down
    	  goDown();
    	  break;
    	}
      }
	});

    $scope.is_tag_visible_in_list = function(tag){
      return _.contains(metadata.tag_visible_in_list, tag);
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




    $scope.removeFromList = function(episode_id){
      delete $scope.episodes[episode_id];
      $scope.rows = $scope.getVisibleEpisodes();
      $scope.num_episodes -= 1;
      $scope.episode = $scope.rows[0];
    }


    $scope.newNamedItem = function(episode, name) {
      return episode.recordEditor.newItem(name);
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

      if(iix === episode[name].length){
        episode.recordEditor.newItem(name);
      }
      else{
        var item = episode[name][iix];

        episode.recordEditor.editItem(name, item).then(function(result){
          reset_state(result);
        });
      }
    };

	function getEpisode(rix) {
	  return $scope.rows[rix];
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
