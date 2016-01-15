angular.module('opal.controllers').controller(
    'EpisodeDetailCtrl', function($scope, $modal, $cookieStore, $location,
                                  $rootScope, RecordEditor,
                                  Flow, EpisodeDetailMixin,
                                  episode, options, profile) {
          $scope._ = _;
    	    $rootScope.state = 'normal';
          $scope.url = $location.url();
          $scope.Flow = Flow;
    	    $scope.episode = episode;
          $scope.options = options;
          $scope.profile =  profile;
          $scope.tag_display = options.tag_display;
          var recordEditor = new RecordEditor(options, profile);

          $scope.is_tag_visible_in_list = function(tag){
              return _.contains(options.tag_visible_in_list, tag);
          };

          $scope.deleteItem = function(name, iix){
              return recordEditor.deleteItem(episode, name, iix, $rootScope);
          };

          $scope.editNamedItem = function(name, iix){
              return recordEditor.editItem(episode, name, iix, $scope, $rootScope);
          };

          $scope.newNamedItem = function(name){
              return recordEditor.editItem(episode, name, $scope, $rootScope);
          }

          EpisodeDetailMixin($scope);
    });
