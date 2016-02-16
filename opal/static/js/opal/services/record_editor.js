angular.module('opal.services').factory('RecordEditor', function($http, $q, Item, $modal, $rootScope, UserProfile){
  "use strict";
  var RecordEditor = function(episode){
    var self = this;
    // self.options = options;
    // self.profile = profile;
    self.emptyPromise = function(){
        // if its read only, just return an empty promise
        var empty = $q.defer();
        empty.resolve();
        return empty.promise;
    }

    self.deleteItem = function(name, iix){
      if(profile.readonly){
          return self.emptyPromise();
      }

      var item = self.getItem(name, iix);

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

      $rootScope.state = 'modal';
      var deferred = $q.defer();

      var modal = $modal.open({
        templateUrl: '/templates/modals/delete_item_confirmation.html/',
        controller: 'DeleteItemConfirmationCtrl',
        resolve: {
          item: function() { return item; }
        }
      }).result.then(function(result) {
        $$rootScope.state = 'normal';
        deferred.resolve(result);
      });

      return deferred.promise;
    };

    self.getItem = function(name, iix){
      if (episode[name][iix] && episode[name][iix].columnName) {
          return episode[name][iix];
      } else {
          return new Item(episode[name][iix], episode, $rootScope.fields[name]);
      }
    };

    self.openEditItemModal = function(item, name, tags){
      $rootScope.state = 'modal';
      var template_url = '/templates/modals/' + name + '.html/';
      template_url += tags.currentTag + '/' + tags.currentSubTag;

      var modal_opts = {
          backdrop: 'static',
          templateUrl: template_url,
          controller: 'EditItemCtrl',
          resolve: {
              item: function() { return item; },
              options: function(Options) { return Options; },
              profile: function(UserProfile) { return UserProfile; },
              episode: function() { return episode; }
          }
      };

      if(item.size){
          modal_opts.size = item.size;
      }else{
          modal_opts.size = 'lg';
      }

      var modal = $modal.open(modal_opts);

      var deferred = $q.defer();

      modal.result.then(function(result) {
        $rootScope.state = 'normal';
        deferred.resolve(result);
      });

      return deferred.promise;
    };

    self.editItem = function(name, iix, tags){
      if(self.profile.readonly){
          return self.emptyPromise();
      }

      var item = self.getItem(name, iix);
      return self.openEditItemModal(episode, item, name, tags);
    };

    self.newItem = function(name, tags){
      if(self.profile.readonly){
          return self.emptyPromise();
      }

      if (!episode[name]) {
          episode[name] = [];
      }

      var iix;
      var item = self.getItem(episode, name, iix);
      episode[name].push(item);
      return self.openEditItemModal(episode, item, name, tags);
    };
  };

  return RecordEditor;
});
