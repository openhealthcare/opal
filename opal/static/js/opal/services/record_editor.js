angular.module('opal.services').factory('RecordEditor', function($http, $q, Item, $modal, $rootScope, UserProfile){
  "use strict";
  var RecordEditor = function(episode){
    var self = this;

    self.deleteItem = function(name, iix){

      var item = self.getItem(name, iix);
      var deferred = $q.defer();

      if (!angular.isDefined(item) || item.isReadOnly() || item.isSingleton()) {
        // Cannot delete 'Add'
        deferred.resolve();
        return deferred.promise;
      }

      $rootScope.state = 'modal';

      UserProfile.then(function(profile){
        if(profile.readonly){
            deferred.resolve();
            return deferred.promise;
        }

        var modal = $modal.open({
          templateUrl: '/templates/modals/delete_item_confirmation.html/',
          controller: 'DeleteItemConfirmationCtrl',
          resolve: {
            item: function() { return item; },
            profile: function(){ return profile; }
          }
        }).result.then(function(result) {
          $rootScope.state = 'normal';
          deferred.resolve(result);
        });
      });

      return deferred.promise;
    };

    self.getItem = function(name, iix){
      if (episode[name][iix] && episode[name][iix].columnName) {
          return episode[name][iix];
      } else {
          return episode.newItem(name, {column: $rootScope.fields[name]});
      }
    };

    self.openEditItemModal = function(item, name, tags){
      $rootScope.state = 'modal';

      var template_url = '/templates/modals/' + name + '.html/';

      if(tags){
        template_url += tags.currentTag + '/' + tags.currentSubTag;
      }

      var deferred = $q.defer();

      UserProfile.then(function(profile){
        if(profile.readonly){
            deferred.resolve();
        }
        else{
          var modal_opts = {
              backdrop: 'static',
              templateUrl: template_url,
              controller: 'EditItemCtrl',
              resolve: {
                  item: function() { return item; },
                  options: function(Options) { return Options; },
                  profile: function(UserProfile) { return profile; },
                  episode: function() { return episode; }
              }
          };

          if(item.size){
              modal_opts.size = item.size;
          }else{
              modal_opts.size = 'lg';
          }

          var modal = $modal.open(modal_opts);

          modal.result.then(function(result) {
            $rootScope.state = 'normal';
            deferred.resolve(result);
          });
        }
      });

      return deferred.promise;
    };

    self.editItem = function(name, iix, tags){
      var item = self.getItem(name, iix);
      return self.openEditItemModal(item, name, tags);
    };

    self.newItem = function(name, tags){
      if (!episode[name]) {
          episode[name] = [];
      }

      var iix = episode[name].length;
      var item = self.getItem(name, iix);

      if(item.isReadOnly() || item.isSingleton()){
        var deferred = $q.defer();
        deferred.resolve();
        return deferred.promise;
      }
      episode[name].push(item);
      return self.openEditItemModal(item, name, tags);
    };
  };

  return RecordEditor;
});
