angular.module('opal.services').factory('RecordEditor', function($http, $q, Item, $modal){
  "use strict";
  var RecordEditor = function(options, profile){
    var self = this;
    self.options = options;
    self.profile = profile;

    self.emptyPromise = function(){
        // if its read only, just return an empty promise
        var empty = $q.defer();
        empty.resolve();
        return empty.promise;
    }

    self.deleteItem = function(episode, name, iix, rootScope){
      if(profile.readonly){
          return self.emptyPromise();
      }

      var item = self.getItem(episode, name, iix, rootScope);

      if (!angular.isDefined(item)) {
        // Cannot delete 'Add'
        return;
      }

      if(!item.isReadOnly){
          item = new Item(column_name, episode, rootScope.fields[column_name]);
      }

      if (item.isReadOnly()) {
          // Cannont delete readonly columns
          return;
      }

      if (item.isSingleton()) {
        // Cannot delete singleton
        return;
      }

      rootScope.state = 'modal';
      var deferred = $q.defer();

      var modal = $modal.open({
        templateUrl: '/templates/modals/delete_item_confirmation.html/',
        controller: 'DeleteItemConfirmationCtrl',
        resolve: {
          item: function() { return item; }
        }
      }).result.then(function(result) {
        $rootScope.state = 'normal';
        deferred.resolve(result);
      });

      return deferred.promise;
    };

    self.getItem = function(episode, name, iix, rootScope){
      if (episode[name][iix] && episode[name][iix].columnName) {
          return episode[name][iix];
      } else {
          return new Item(episode[name][iix], episode, rootScope.fields[name]);
      }
    };

    self.openEditItemModal = function(episode, item, name, scope, rootScope){
      rootScope.state = 'modal';
      var template_url = '/templates/modals/' + name + '.html/';
      template_url += scope.currentTag + '/' + scope.currentSubTag;

      var modal_opts = {
          backdrop: 'static',
          templateUrl: template_url,
          controller: 'EditItemCtrl',
          resolve: {
              item: function() { return item; },
              options: function() { return self.options; },
              profile: function() { return self.profile; },
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
        rootScope.state = 'normal';
        deferred.resolve(result);
      });

      return deferred.promise;
    };

    self.editItem = function(episode, name, iix, scope, rootScope){
      if(self.profile.readonly){
          return self.emptyPromise();
      }

      var item = self.getItem(episode, name, iix, rootScope);
      return self.openEditItemModal(episode, item, name, scope, rootScope);
    };

    self.newItem = function(episode, name, scope, rootScope){
      if(self.profile.readonly){
          return self.emptyPromise();
      }

      if (!episode[name]) {
          episode[name] = [];
      }

      var iix;
      var item = self.getItem(episode, name, iix, rootScope);
      episode[name].push(item);
      return self.openEditItemModal(episode, item, name, scope, rootScope);
    };
  };

  return RecordEditor;
});
